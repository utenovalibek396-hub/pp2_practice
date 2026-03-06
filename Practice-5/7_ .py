import re
text = input("Enter a snake_case string: ")
parts = text.split('_')
camel_case = parts[0] + ''.join(word.capitalize() for word in parts[1:])
print(camel_case)

