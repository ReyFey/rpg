from Person import *
from Player import *
from Role import *


class Personnage(Person):
    def __init__(self, id: int, player: Player, name: str, sexe: str, age: int, role: Role):
        super().__init__(id, name, age)
        self.player = player
        self.sexe = sexe
        self.role = role
        self.pv = role.pv
        self.pa = role.pa
        self.pm = role.pm
        self.mana = role.mana
