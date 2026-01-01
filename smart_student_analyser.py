def Marks():
    marks={}
    n=int(input("enter no of subjects:"))
    for i in range(n):
        subject=input("enter subject name:")
        score=int(input(f"enter score for {subject}:"))
        marks[subject]=score
    return marks

#Calculate Average
def Average(marks):
    total=0
    for score in marks.values():
        total+=score
    return total/len(marks)

#Grade Calculation
def Grade(avg):
    if avg>=90:
        return "A"
    elif avg>=75:
        return "B"
    elif avg>=60:
        return "C"
    elif avg>=40:
        return "D"
    else:
        return "F"

#cheking pass/fail
def check_pass_fail(marks):
    for score in marks.values():
        if score<35:
            return "Fail"
    return "Pass"

#Identify Weak Subjects
def find_weak_subjects(marks):
    weak=[]
    for subject,score in marks.items():
        if score<50:
            weak.append(subject)
    return weak
#Report Generation(Output)
def generate_report(marks):
    avg=Average(marks)
    grade=Grade(avg)
    result=check_pass_fail(marks)
    weak_subjects=find_weak_subjects(marks)

    print("\n------Performance Report-------")
    print("Marks=",marks)
    print("Grade=",grade)
    print("Result=",result)

    if weak_subjects:
        print("Weak Subjects:"," ,".join(weak_subjects))
    else:
        print("No weak subjects.Excellent!")
marks=Marks()
generate_report(marks)


    
    
    




    
        
     
    
        
    

