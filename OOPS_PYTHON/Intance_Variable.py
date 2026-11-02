class Dog:
    animal = "dog"

    def __init__(self, breed):
        self.breed = breed

    def get_breed(self):
        print("Breed is:", self.breed)


Rodger = Dog("Pug")
Bruno = Dog("Bulldog")

Rodger.get_breed()
Bruno.get_breed()