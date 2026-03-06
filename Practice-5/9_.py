import re
text = input("Enter a string: ")
result = re.sub(r"([A-Z])", r" \1", text)
result = result.lstrip()
print(result)
