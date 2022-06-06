from Person import *


class Personnage(Person):
    def __init__(self, id, player, name, sexe, age, role):
        super().__init__(id, name, age)
        self.player = player
        self.sexe = sexe
        self.role = role
        self.pv = role.pv
        self.pa = role.pa
        self.pm = role.pm
        self.mana = role.mana
