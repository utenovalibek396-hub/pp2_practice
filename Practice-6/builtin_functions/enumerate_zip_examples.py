#1
from functools import reduce #reduce is function, functools is module
nums = [1, 2, 3, 4]
total = reduce(lambda x, y: x + y, nums) #lambda is anonymous function
print(total)
#reduce() is used to apply a function of two arguments cumulatively to the items of a sequence.
#2
names = ["Ali", "Aruzhan", "Dana"]
for i, name in enumerate(names): #enumerate returns index and value of the list
    print(i, name)
#3
names = ["Ali", "Dana"]
scores = [90, 85]
for name, score in zip(names, scores): #zip returns pairs of elements from two lists
    print(name, score)
