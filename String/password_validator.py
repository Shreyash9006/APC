password = input("Enter password: ")

has_upper = any(ch.isupper() for ch in password)
has_lower = any(ch.islower() for ch in password)
has_digit = any(ch.isdigit() for ch in password)
has_special = any(not ch.isalnum() for ch in password)

if len(password) >= 8 and has_upper and has_lower and has_digit and has_special:
    print("Valid Password")
else:
    print("Invalid Password")