s = input("Enter a string: ")

result = ""
i = 0

while i < len(s):
    count = s.count(s[i])
    
    result += s[i] + str(count)
    i += count

print("Compressed =", result)