n = int(input())
if n < 1:
    print("Not prime")
else:
    i = 2
    while i < n:
        if n % i == 0:
            print("Not prime")
            break
        i+=1    
    else:
        print("Prime")
        
