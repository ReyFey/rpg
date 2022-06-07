class Role:
    def __init__(self, id: int, label: str, pv: int, pa: int, pm: int, mana: int):
        self.id = id
        self.label = label
        self.pv = pv
        self.pa = pa
        self.pm = pm
        self.mana = mana
        self.personnages = []
