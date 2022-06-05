from Person import *


class Player(Person):
    def __init__(self, name, age):
        super().__init__(name, age)
        self.personnages = []
