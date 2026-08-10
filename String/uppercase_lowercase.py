s = input("Enter a string: ")

uppercase = 0
lowercase = 0

for ch in s:
    if ch.isupper():
        uppercase += 1
    elif ch.islower():
        lowercase += 1

print("Uppercase =", uppercase)
print("Lowercase =", lowercase)