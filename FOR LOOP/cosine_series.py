import math

x = float(input("Enter x: "))
n = int(input("Enter n: "))

sum = 1

for i in range(2, n + 1, 2):
    term = (x ** i) / math.factorial(i)

    if (i // 2) % 2 == 1:
        sum -= term
    else:
        sum += term

print("Cos(x) =", sum)