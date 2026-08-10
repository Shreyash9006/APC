email = input("Enter email: ")

if email.count("@") == 1 and "." in email.split("@")[1]:
    print("Valid Email")
else:
    print("Invalid Email")