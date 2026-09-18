import os
from dotenv import load_dotenv
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash


load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")


def get_db():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "student_analyzer"),
        ssl_verify_cert=False
    )

def calculate_average(marks):
    return round(sum(marks.values()) / len(marks), 2) if marks else 0


def calculate_grade(avg):
    if avg >= 90:
        return "A"
    elif avg >= 75:
        return "B"
    elif avg >= 60:
        return "C"
    elif avg >= 40:
        return "D"
    return "F"


def check_pass_fail(marks):
    return "Fail" if any(score < 35 for score in marks.values()) else "Pass"


def find_weak_subjects(marks):
    return [subject for subject, score in marks.items() if score < 50]


def get_recommendation(avg, result, weak_subjects):
    if result == "Fail":
        return "Focus on failed subjects and strengthen the basics before moving to advanced topics."
    if weak_subjects:
        return f"Give extra attention to {', '.join(weak_subjects)} and practice them regularly."
    if avg >= 90:
        return "Excellent performance! Keep maintaining this consistency."
    if avg >= 75:
        return "Very good performance. More practice can help you reach the next level."
    if avg >= 60:
        return "Good start. Focus on weaker areas to improve your overall score."
    return "Practice regularly and revise the fundamentals."


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 6:
            flash("Enter all fields. Password must contain at least 6 characters.", "error")
            return render_template("register.html")

        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("An account with this email already exists.", "error")
                return render_template("register.html")

            password_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (name, email, password_hash)
            )
            db.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        except Error as e:
            flash(f"Database error: {e}", "error")
        finally:
            try:
                cursor.close()
                db.close()
            except Exception:
                pass

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                return redirect(url_for("dashboard"))

            flash("Invalid email or password.", "error")
        except Error as e:
            flash(f"Database error: {e}", "error")
        finally:
            try:
                cursor.close()
                db.close()
            except Exception:
                pass

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, average, grade, result, created_at
            FROM reports
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (session["user_id"],))
        reports = cursor.fetchall()
        return render_template("dashboard.html", reports=reports)
    except Error as e:
        flash(f"Database error: {e}", "error")
        return render_template("dashboard.html", reports=[])
    finally:
        try:
            cursor.close()
            db.close()
        except Exception:
            pass


@app.route("/analyze", methods=["GET", "POST"])
@login_required
def analyze():
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip() or session.get("user_name", "Student")
        subjects = request.form.getlist("subject[]")
        scores = request.form.getlist("score[]")
        marks = {}
        errors = []

        for subject, score in zip(subjects, scores):
            subject = subject.strip()
            if not subject:
                continue
            try:
                score = float(score)
            except ValueError:
                errors.append(f"Invalid mark for {subject}.")
                continue

            if score < 0 or score > 100:
                errors.append(f"Marks for {subject} must be between 0 and 100.")
                continue

            if subject in marks:
                errors.append(f"Duplicate subject: {subject}.")
                continue

            marks[subject] = score

        if not marks:
            errors.append("Enter at least one valid subject.")

        if errors:
            return render_template("analyze.html", errors=errors, old_name=student_name)

        average = calculate_average(marks)
        grade = calculate_grade(average)
        result = check_pass_fail(marks)
        weak_subjects = find_weak_subjects(marks)
        recommendation = get_recommendation(average, result, weak_subjects)

        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO reports (user_id, student_name, average, grade, result, recommendation) VALUES (%s,%s,%s,%s,%s,%s)",
                (session["user_id"], student_name, average, grade, result, recommendation)
            )
            report_id = cursor.lastrowid

            for subject, score in marks.items():
                cursor.execute(
                    "INSERT INTO subject_marks (report_id, subject_name, score) VALUES (%s,%s,%s)",
                    (report_id, subject, score)
                )
            db.commit()
        except Error as e:
            flash(f"Could not save report: {e}", "error")
            return render_template("analyze.html", errors=[], old_name=student_name)
        finally:
            try:
                cursor.close()
                db.close()
            except Exception:
                pass

        return render_template(
            "result.html",
            student_name=student_name,
            marks=marks,
            average=average,
            grade=grade,
            result=result,
            weak_subjects=weak_subjects,
            recommendation=recommendation,
            report_id=report_id
        )

    return render_template("analyze.html", errors=[])


@app.route("/report/<int:report_id>")
@login_required
def report(report_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM reports WHERE id = %s AND user_id = %s",
            (report_id, session["user_id"])
        )
        report_data = cursor.fetchone()
        if not report_data:
            flash("Report not found.", "error")
            return redirect(url_for("dashboard"))

        cursor.execute(
            "SELECT subject_name, score FROM subject_marks WHERE report_id = %s ORDER BY id",
            (report_id,)
        )
        rows = cursor.fetchall()
        marks = {row["subject_name"]: float(row["score"]) for row in rows}
        weak_subjects = find_weak_subjects(marks)

        return render_template(
            "result.html",
            student_name=report_data["student_name"],
            marks=marks,
            average=float(report_data["average"]),
            grade=report_data["grade"],
            result=report_data["result"],
            weak_subjects=weak_subjects,
            recommendation=report_data["recommendation"],
            report_id=report_id
        )
    except Error as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for("dashboard"))
    finally:
        try:
            cursor.close()
            db.close()
        except Exception:
            pass


@app.route("/delete-report/<int:report_id>", methods=["POST"])
@login_required
def delete_report(report_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM reports WHERE id = %s AND user_id = %s",
            (report_id, session["user_id"])
        )
        db.commit()
        flash("Report deleted.", "success")
    except Error as e:
        flash(f"Database error: {e}", "error")
    finally:
        try:
            cursor.close()
            db.close()
        except Exception:
            pass
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
