n = int(input())
summa = 0
for i in range(1,n+1):
    if i % 5 == 0:
        break
    if i % 3 == 0:
        continue
    summa += i
    
print(summa)