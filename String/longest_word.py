s = input("Enter a sentence: ")

words = s.split()

longest = max(words, key=len)

print("Longest word =", longest)