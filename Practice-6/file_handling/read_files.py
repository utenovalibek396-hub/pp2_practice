import os #import os module to work with directories
os.makedirs("root/level1/level2", exist_ok=True) #os.nakedirs creates directories.
with open("root/file1.txt", "w") as f:
    f.write("file1")
with open("root/level1/file2.py", "w") as f:
    f.write("file2")
for root, dirs, files in os.walk("root"):
    print("DIR:", root)
    for d in dirs:
        print("  folder:", d)
    for f in files:
        print("  file:", f)
ext = ".py"
found = []
for root, dirs, files in os.walk("root"): #os.walk generates the filelist in the directory tree by walking either top-down or bottom-up through the directory tree
    for f in files:
        if f.endswith(ext): #f.endswith checks if the file name ends with the specified extension
            found.append(os.path.join(root, f))
print("FOUND:", found)
