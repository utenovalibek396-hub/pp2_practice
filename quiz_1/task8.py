class Calculator:
    def __init__(self,a,b):
        self.a = a
        self.b = b
    def add(self):
        return self.a + self.b
    def difference(self):
        return self.a - self.b, self.b - self.a
    def multiply(self):
        return self.a * self.b
    def divided(self):
        return self.a / self.b, self.b / self.a
a = int(input())
b = int(input())
g = input()

if g == "add":
    x = Calculator(a,b)
    print(x.add())
elif g == "difference":
    x = Calculator(a,b)
    print(x.difference())
elif g == "multiply":
    x = Calculator(a,b)
    print(x.multiply())
elif g == "divided":
    x = Calculator(a,b)
    print(x.divided())
else:
    print("Error")        