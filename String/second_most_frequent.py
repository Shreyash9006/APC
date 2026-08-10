s = input("Enter a string: ")

characters = set(s)

frequency = []

for ch in characters:
    frequency.append((ch, s.count(ch)))

frequency.sort(key=lambda x: x[1], reverse=True)

if len(frequency) >= 2:
    print("Second most frequent character =", frequency[1][0])
    print("Frequency =", frequency[1][1])
else:
    print("Second most frequent character does not exist")