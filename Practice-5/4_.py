import re
pattern = r"^[A-Z][a-z]+$"
text = input("Enter a string: ")
if re.match(pattern, text):
    print("Yes")
else:
    print("No")
