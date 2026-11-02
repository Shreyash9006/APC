class Dog:
    animal = "dog"

    def __init__(self, breed, color):
        self.breed = breed
        self.color = color

    def get_details(self):
        print("Breed is:", self.breed)
        print("Color is:", self.color)

    def get_animal(self):
        print("Animal is:", self.animal)


Rodger = Dog("Pug", "brown")
Bruno = Dog("Bulldog", "black")

print(Rodger.animal)
print(Bruno.animal)