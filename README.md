# Smart Student Analyzer — Full Stack

A full-stack student performance analysis web application built with Python Flask, MySQL, HTML, CSS and JavaScript.

## Features

- User registration and login
- Secure password hashing
- Student performance analysis
- Dynamic subject/mark entry
- Average and grade calculation
- Pass/fail checking
- Weak-subject identification
- Personalized recommendations
- MySQL report history
- Dashboard showing previous reports
- View and delete saved reports
- Responsive UI
- Input validation
- Parameterized SQL queries

## Tech Stack

- Python
- Flask
- MySQL
- HTML5
- CSS3
- JavaScript
- Jinja2
- Werkzeug password hashing

## Setup

### 1. Install Python

Make sure Python is installed and available in VS Code.

### 2. Create virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL

Open MySQL Workbench or the MySQL command line and run:

```text
database.sql
```

This creates the `student_analyzer` database and its tables.

### 5. Configure database credentials

Copy `.env.example` to `.env` and change the values.

For example:

```text
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=student_analyzer
```

### 6. Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Main Application Flow

```text
User
  ↓
Login/Register
  ↓
Dashboard
  ↓
Enter Student Marks
  ↓
Flask Route
  ↓
Python Analysis Functions
  ↓
Save Report to MySQL
  ↓
Performance Dashboard
  ↓
Report History
```

## Database Design

### users

Stores account details.

### reports

Stores each performance report.

### subject_marks

Stores subject-wise marks belonging to a report.

Relationship:

```text
users 1 ─────── many reports
reports 1 ───── many subject_marks
```

## GitHub

Do NOT upload:

- `.env`
- `venv/`
- passwords
- secret keys

The included `.gitignore` protects these files.

## Future Improvements

- PDF report download
- Performance charts
- Search/filter reports
- Admin dashboard
- Email report
- Deployment using a cloud platform
- REST API
- Role-based access
