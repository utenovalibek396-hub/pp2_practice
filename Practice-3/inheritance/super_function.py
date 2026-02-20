class Animal:
    def __init__(self,name):
        self.name = name
class Dog(Animal):
    def __init__(self, name):
        super().__init__(name)
d = Dog("Aktos")
print(d.name)
#It avoids repeating code from the parent class.

#It ensures that the parent class is properly initialized.

#It works in single and multiple inheritance situations.
