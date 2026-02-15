class Greet:
    def __init__(self,person):
        self.person = person
    def greet(self):
        return self.person
z = input().split()
y = z[0] + " "+ z[1]
x = Greet(y)
print(x.greet())
