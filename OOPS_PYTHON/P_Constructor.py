class Demo:
    def __init__(self, first, second):
        self.first = first
        self.second = second
        self.answer = 0

    def display(self):
        print("First number =", self.first)
        print("Second number =", self.second)
        print("Addition of two numbers =", self.answer)

    def calculate(self):
        self.answer = self.first + self.second


obj = Demo(1000, 2000)
obj.calculate()
obj.display()