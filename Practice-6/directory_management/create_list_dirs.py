import os
dirs = ["folder1", "folder2", "folder3"]
for d in dirs:
    os.makedirs(d, exist_ok=True)
for item in os.listdir():
    if os.path.isdir(item):
        print(item)
#import os module to work with directories
#makedirs creates directories, exist_ok=True allows to create directory if it already exists
#listdir returns list of items in the current directory
#isdir checks if the item is a directory
