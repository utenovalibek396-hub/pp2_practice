import re
text = input("Enter a camelCase string: ")
snake_case = re.sub(r'([A-Z])', r'_\1', text).lower()
snake_case = snake_case.lstrip('_')
print(snake_case)
