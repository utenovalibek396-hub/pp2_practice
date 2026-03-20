import os
import shutil
os.makedirs("source", exist_ok=True)
os.makedirs("destination", exist_ok=True)
file_path = os.path.join("source", "test.txt")
with open(file_path, "w") as f:
    f.write("This file will be moved.")
shutil.move(file_path, os.path.join("destination", "test.txt"))
print(os.listdir("destination"))
#import os module to work with directories
#import shutil module to move files
#makedirs creates directories, exist_ok=True allows to create directory if it already exists
#join creates a path by joining directory and file name