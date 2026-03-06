import re
pattern = r'\b[a-z]+_[a-z]+\b'
text = input()
if re.search(pattern, text):
    print("Yes")
else:
    print("No")