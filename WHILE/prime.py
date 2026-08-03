n = int(input("Enter a number: "))
i = 2
count = 0

while i < n:
    if n % i == 0:
        count += 1
    i += 1

if count == 0 and n > 1:
    print("Prime")
else:
    print("Not Prime")