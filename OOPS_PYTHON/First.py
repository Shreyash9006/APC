class Student:
    def get(self):
        self.name = input("Enter student name: ")
        self.roll_no = input("Enter roll number: ")
        self.branch = input("Enter branch: ")
        self.marks = float(input("Enter marks: "))

    def display(self):
        print("\nStudent Information")
        print("Name:", self.name)
        print("Roll No:", self.roll_no)
        print("Branch:", self.branch)
        print("Marks:", self.marks)


student = Student()

student.get()
student.display()