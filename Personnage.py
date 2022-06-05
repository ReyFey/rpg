from Person import *


class Personnage(Person):
    def __init__(self, player, name, sexe, age, role):
        super().__init__(name, age)
        self.player = player
        self.sexe = sexe
        self.role = role
