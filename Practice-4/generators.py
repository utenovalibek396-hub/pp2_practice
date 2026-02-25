def even(n):
    for i in range(n+1):
        if i % 2 == 0:
            yield i
n = int(input())
for i in even(n):
    print(i)
#This defines a generator function named even. It will generate even numbers up to n
#Third line checks if the number is even.
#yield returns the number one by one.This makes the function a generator, not a normal function.