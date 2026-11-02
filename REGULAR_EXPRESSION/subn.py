import re

string = "Java is easy. Java is powerful."

result = re.subn("Java", "Python", string)

print(result)