list = list(map(int,input().split()))
def summ(list):
    summa = 0
    for i in range(len(list)):
        summa += list[i]
    return summa
print(summ(list))
