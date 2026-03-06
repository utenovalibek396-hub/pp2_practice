import re
pattern = r"^a.*b$"
text = input("Enter a string: ")
if re.match(pattern, text):
    print("Yes")
else:
    print("No")
