import  re
text = input("Enter a string: ")
parts = re.split(r'(?=[A-Z])', text)
print(parts)

