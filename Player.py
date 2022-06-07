from Person import *


class Player(Person):
    def __init__(self, id: int, name: str, age: int):
        super().__init__(id, name, age)
        self.characters = []
