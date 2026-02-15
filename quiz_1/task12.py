numbers = []
while True:
    n = int(input())
    numbers.append(n)
    if n == 0:
        break
z = numbers[:len(numbers)-1]
t = 1
for i in range(len(z)):
    if z[i] < 0:
        continue
    if z[i] % 2 == 0:
        t*=z[i]
print(t)