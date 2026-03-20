import os   #import os module to work with directories
import shutil #import shutil module to move files
os.makedirs("src", exist_ok=True) 
os.makedirs("dst", exist_ok=True)
#makedirs creates directories, exist_ok=True allows to create directory if it already exists
with open("src/test.txt", "w") as f:
    f.write("copy me")
shutil.copy("src/test.txt", "dst/test.txt") #shutil.copy copies the file from source to destination
shutil.move("src/test.txt", "dst/moved_test.txt") #shutil.move moves the file from source to destination
print(os.listdir("dst")) #listdir returns list of items in the specified directory
file_to_delete = "dst/test.txt"
if os.path.exists(file_to_delete): #os.path.exists checks if the file exists
    os.remove(file_to_delete) #os.remove deletes the specified file
print(os.listdir("dst")) #listdir returns list of items in the specified directory