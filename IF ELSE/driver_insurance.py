married = input("Are you married? (yes/no): ").lower()

if married == "yes":
    print("Driver is insured")
else:
    gender = input("Enter gender (male/female): ").lower()
    age = int(input("Enter age: "))

    if (gender == "male" and age > 30) or (gender == "female" and age > 25):
        print("Driver is insured")
    else:
        print("Driver is not insured")