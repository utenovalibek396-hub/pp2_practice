import json 
x = {
  "name": "John",
  "age": 30,
  "city": "New York"
}
y = json.dumps(x)
print(y)
# This line imports the json module, which is used to work with JSON data in Python.
# This creates a Python dictionary with three key-value pairs.
# json.dumps() converts the Python dictionary into a JSON string.