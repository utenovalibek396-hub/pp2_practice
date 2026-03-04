#Task 1
import re
pattern = r"^ab*$"
text = input("Enter a string: ")
if re.match(pattern, text):
    print("Yes")
else:
    print("No")

#Task 2
pattern = r"^ab{2,3}$"
text = input("Enter a string: ")
if re.match(pattern, text):
    print("Yes")
else:
    print("No")


#Task 3
pattern = r"^[a-z]+_[a-z]+$"
text = input("Enter a string: ")
if re.match(pattern, text):
    print("Yes")
else:
    print("No")



#Task 4
pattern = r"^[A-Z][a-z]+$"
text = input("Enter a string: ")
if re.match(pattern, text):
    print("Yes")
else:
    print("No")


#Task 5
pattern = r"^a.*b$"
text = input("Enter a string: ")
if re.match(pattern, text):
    print("Yes")
else:
    print("No")


#Task 6
text = input("Enter a string: ")
result = re.sub(r"[ ,\.]", ":", text)
print(result)


#Task 7
text = input("Enter a snake_case string: ")
parts = text.split('_')
camel_case = parts[0] + ''.join(word.capitalize() for word in parts[1:])
print(camel_case)



#Task 8
text = input("Enter a string: ")
parts = re.split(r'(?=[A-Z])', text)
print(parts)


#Task 9
text = input("Enter a string: ")
result = re.sub(r"([A-Z])", r" \1", text)
result = result.lstrip()
print(result)


#Task 10
text = input("Enter a camelCase string: ")
snake_case = re.sub(r'([A-Z])', r'_\1', text).lower()
snake_case = snake_case.lstrip('_')
print(snake_case)