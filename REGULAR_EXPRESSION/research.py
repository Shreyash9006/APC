import re

s = "Dypcet kolhapur department of CSE"

match = re.search("depart", s)

print("Start Index:", match.start())
print("End Index:", match.end())