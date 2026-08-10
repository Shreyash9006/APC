s = input("Enter a sentence: ")

words = s.split()

shortest = min(words, key=len)

print("Shortest word =", shortest)