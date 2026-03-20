import os #import os module to work with directories
os.makedirs("data", exist_ok=True) #os.makedirs creates directories, exist_ok=True allows to create directory if it already exists
with open("data/sample.txt", "w") as f:
    f.write("Hello\n")
with open("data/sample.txt", "a") as f:
    f.write("World\n")
with open("data/sample.txt", "r") as f:
    print(f.read())
