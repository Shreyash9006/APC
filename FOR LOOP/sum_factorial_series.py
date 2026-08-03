n = int(input("Enter n: "))

fact = 1
s = 1

for i in range(1, n + 1):
    fact *= i
    s += 1 / fact

print("Sum =", s)