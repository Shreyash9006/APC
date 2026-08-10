paragraph = input("Enter paragraph: ")

words = paragraph.lower().split()

for word in set(words):
    print(word, "=", words.count(word))