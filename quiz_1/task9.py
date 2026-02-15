numbers = []
while True:
    n = int(input())
    numbers.append(n)
    if n == 0:
        break
for i in range(len(numbers)):
    if numbers[i] < 1:
        continue
    else:
        for j in range(2,numbers[i]):
            if numbers[i] % j == 0:
                break
        else:
            print(numbers[i])
            break
  