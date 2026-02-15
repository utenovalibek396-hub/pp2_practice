def evens(n):
    for i in range(0,n+1):
        if i % 2 == 0:
            print(i,end=" ")
n = int(input())
evens(n)
