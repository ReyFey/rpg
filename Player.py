from Person import *


class Player(Person):
    def __init__(self, id, name, age):
        super().__init__(id, name, age)
        self.personnages = []
