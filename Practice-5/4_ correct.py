import re
pattern = r"\b[A-Z][a-z]+\b"
text = input("Enter a string: ")
if re.search(pattern, text):
    print("Yes")
else:
    print("No")
