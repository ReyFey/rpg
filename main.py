import json
from typing import Optional

from Database import *
from Character import *
from Role import *

# Database
with open('database.json', 'r') as database_file:
    database_data = json.load(database_file)

try:
    database = Database(database_data["host"],
                        database_data["port"],
                        database_data["user"],
                        database_data["password"],
                        database_data["name"])
except():
    print("Impossible de se connecter à la base de données")
else:
    print("Base de données connectée")

# Initialization
is_running = True
dead_player = Player(0, "dead", 0)
default_player = Player(0, "default", 0)
active_player = default_player
default_role = Role(0, "default", 0, 0, 0, 0)
default_char = Character(0, active_player, "default", 'M', 0, default_role)
character_played = default_char
insert_counter_players = 0
insert_counter_chars = 0
players = []
characters = []
roles = []


# Fetch data
def fetch():
    global insert_counter_players
    global insert_counter_chars
    try:
        insert_counter_players += database.select("player", ["MAX(id)"])[0][0]
        insert_counter_chars += database.select("character", ["MAX(id)"])[0][0]
        for dbrole in database.select("role", ["id", "label", "pv", "pa", "pm", "mana"]):
            roles.append(Role(dbrole[0], dbrole[1], dbrole[2], dbrole[3], dbrole[4], dbrole[5]))
        for dbuser in database.select("player", ["id", "name", "age"]):
            players.append(Player(dbuser[0], dbuser[1], dbuser[2]))
        for dbchar in database.select("character", ["id", "name", "sexe", "age", "role_id",
                                                    "player_id", "pv", "pa", "pm", "mana"]):
            role_id = dbchar[4]
            _role = default_role
            if role_id:
                for role in roles:
                    if role.id == role_id:
                        _role = role
            user = dead_player
            player_id = dbchar[5]
            if player_id:
                for player in players:
                    if player.id == player_id:
                        user = player
            character = Character(dbchar[0], user, dbchar[1], dbchar[2], dbchar[3], _role)
            character.pv = dbchar[6]
            character.pa = dbchar[7]
            character.pm = dbchar[8]
            character.mana = dbchar[9]
            characters.append(character)
            _role.characters.append(character)
            user.characters.append(character)
    except():
        print("Les données n'ont pas pu se charger correctement\n")
    else:
        print("Les données sont chargées\n")


# CRUD Players
def list_players():
    if not players:
        print("\nAucun joueur\n")
        return
    print("Liste des joueurs :")
    for player in players:
        print(f"-> {player.name}")
    print("")


def find_player(name: str) -> Optional[Player]:
    for player in players:
        if player.name == name:
            return player
    return None


def test_default(player: Player) -> bool:
    return player == default_player


def create_player() -> Player:
    global insert_counter_players
    name = input("Quel est ton nom ? ")
    if find_player(name) is not None:
        print("Ce nom est déjà prit\n")
        return default_player
    age = int(input("Quel age as-tu? "))
    insert_counter_players += 1
    player = Player(insert_counter_players, name, age)
    players.append(player)
    print(f"LOCAL:{player.id}")
    database.insert_one("player", ["name", "age"], (name, age))
    print("Joueur créé\n")
    return player


def modify_player():
    choice = -1
    while choice != 'q':
        choice = input("\nMODIFIER LE COMPTE\n"
                       f"{active_player.name}, {active_player.age} ans\n"
                       "- Modifier le nom (n)\n"
                       "- Modifier l'age (a)\n"
                       "- Quitter (q)\n")
        if choice == 'n':
            name = input("Quel est votre nom ? ")
            active_player.name = name
            database.update_one("player", ["name"], f"id = %s", (name, active_player.id))
        if choice == 'a':
            age = int(input("Quel est votre age ? "))
            active_player.age = age
            database.update_one("player", ["age"], f"id = %s", (age, active_player.id))


def delete_player() -> bool:
    if find_player(active_player.name) is None:
        print("Ce joueur n'existe pas\n")
        return False
    choice = input("\nEtes vous sur de vouloir le supprimer (o/n) ? \n")
    if choice == 'o':
        for own_char in active_player.characters:
            delete_char(active_player, own_char)
        players.remove(active_player)
        database.delete_by("player", "id = %s", (active_player.id,))
        logout()
        print("Joueur supprimé\n")
        return True


def connect_player() -> Player:
    global active_player
    name = input("Quel est votre nom ? ")
    test = find_player(name)
    if test is None:
        print("Ce compte n'existe pas\n")
        return default_player
    active_player = test
    print(f"\nBonjour {active_player.name} !\n")
    return active_player


def logout():
    global active_player
    global character_played
    active_player = default_player
    character_played = default_char
    print("Au revoir !\n")


# Roles
def search_role(name: str) -> Role:
    for role in roles:
        if role.label == name:
            return role


def list_roles(player: Player):
    if not roles:
        print("\nAucun role\n")
        return
    for role in roles:
        print(f"\n~~~{role.label.upper()}~~~\n"
              f"{role.pv} points de vie (PV)\n"
              f"{role.pa} points d'attaque (PA)\n"
              f"{role.pm} points de mouvement (PM)\n"
              f"{role.mana} points de magie (Mana)")
        chars = []
        for own_char in player.characters:
            if own_char.role == role:
                chars.append(own_char)
        to_print = "Personnages : "
        if chars:
            to_print += chars[0].name
            for index in range(1, len(chars)):
                to_print += f", {chars[index].name}"
        else:
            to_print += "Aucun"
        print(to_print)


# CRUD Characters
def list_char(player: Player):
    if not player.characters:
        print("\nAucun personnage")
        return
    print("Liste de vos personnages :")
    for own_char in player.characters:
        if own_char.player == player:
            print(f"-> {own_char.name}")


def test_char(player: Player, character: Character) -> Character:
    if not character or character not in characters:
        return default_char
    if character.player == player:
        if character in player.characters:
            return character


def search_char(player: Player, name: str) -> Character:
    for own_char in player.characters:
        if own_char.name == name:
            return own_char


def fiche_char(player: Player, character: Character) -> Character:
    if not test_char(player, character):
        print("Personnage non existant ou non possédé")
        return default_char
    sexe = "Aucun"
    if character.sexe == 'H':
        sexe = "Homme"
    if character.sexe == 'F':
        sexe = "Femme"
    print(
        f"Fiche perso\n"
        f"- Nom : {character.name}\n"
        f"- Sexe : {sexe}\n"
        f"- Age : {character.age} ans\n"
        f"- Role : {character.role.label}\n"
        f"PV={character.pv} PA={character.pa} PM={character.pm} Mana={character.mana}"
    )
    return character


def add_char(player: Player) -> Character:
    global insert_counter_chars
    name = input("Quel est le nom de votre personnage ? ")
    if search_char(player, name):
        print("Ce nom est déjà prit")
        return default_char
    role = search_role(input("Quel est le role de ton personnage ? "))
    if not role:
        print("Ce role n'existe pas\n")
        return default_char
    sexe = input("Votre personnage est-il un homme ou une femme (H/F) ? ")
    if sexe != 'H' and sexe != 'F':
        print("Veuillez bien respecter la syntaxe demandée (H/F)\n")
        return default_char
    age = int(input("Quel est l'age de votre personnage ? "))
    insert_counter_chars += 1
    new_char = Character(insert_counter_chars, player, name, sexe, age, role)
    characters.append(new_char)
    player.characters.append(new_char)
    role.characters.append(new_char)
    print(f"LOCAL:{new_char.id}")
    if not active_player == default_player:
        database.insert_one(
            "character",
            ["player_id", "role_id", "name", "sexe", "age", "pv", "pa", "pm", "mana"],
            (
                player.id, role.id, name, sexe, age, role.pv, role.pa, role.pm, role.mana)
            )
    print("Personnage créé")
    return new_char


def modify_char(player: Player, character: Character):
    if fiche_char(player, character):
        choice = -1
        while choice != 'b':
            choice = input("\nMODIFIER LE PERSONNAGE\n"
                           "- Modifier le nom (n)\n"
                           "- Modifier le sexe (s)\n"
                           "- Modifier l'age (a)\n"
                           "- Retour (b)\n")
            if choice == 'n':
                name = input("Quel est son nom ? ")
                character.name = name
                if not player == default_player:
                    database.update_one("character", ["name"], "id = %s", (name, character.id))
            if choice == 's':
                sexe = input("Quel est son sexe (H/F) ? ")
                if sexe == 'H' or sexe == 'F':
                    character.sexe = sexe
                    if not player == default_player:
                        database.update_one("character", ["sexe"], "id = %s", (sexe, character.id))
                else:
                    print("Veuillez bien respecter la syntaxe demandée (H/F)\n")
            if choice == 'a':
                age = int(input("Quel est son age ? "))
                character.age = age
                if not player == default_player:
                    database.update_one("character", ["age"], "id = %s", (age, character.id))


def delete_char(player: Player, character: Character) -> Character:
    if not test_char(player, character):
        print("Personnage introuvable")
        return default_char
    characters.remove(character)
    player.characters.remove(character)
    character.player = dead_player
    if not player == default_player:
        database.delete_by("character", "id = %s", (character.id,))
    print("Personnage supprimé")
    return character


def donate_char(p_origin: Player, p_target: str, character: Character) -> Character:
    global character_played
    if find_player(p_origin.name) is None and not test_default(p_origin):
        print("Le joueur donateur n'existe pas")
        return default_char
    p_target = find_player(p_target)
    if p_target is None:
        print("Le joueur cible n'existe pas")
        return default_char
    if character == default_char or character not in p_origin.characters:
        print("Ce personnage ne vous appartient pas")
        return default_char
    if character == character_played:
        character_played = default_char
    p_origin.characters.remove(character)
    character.player = dead_player
    p_target.characters.append(character)
    character.player = p_target
    if p_origin == default_player:
        database.insert_one("character", ["id", "player_id", "role_id", "name",
                                          "sexe", "age", "pv", "pa", "pm", "mana"],
                            (character.id, p_target.id, character.role.id, character.name, character.sexe,
                             character.age, character.pv, character.pa, character.pm, character.mana)
                            )
    else:
        database.update_one("character", ["player_id"], f"id = %s", (p_target.id, character.id))
    print("Personnage donné avec succès")
    return character


def char():
    global character_played
    choice = -1
    while choice != 'q':
        if test_default(active_player):
            print("\n[Non connecté]")
        else:
            print(f"\n[{active_player.name}]")
        if character_played == default_char:
            print("Veuillez choisir un personnage pour jouer")
        else:
            print(f"Vous avez choisi {character_played.name}")
        choice = input("===========PERSONNAGES===========\n"
                       "- Choisir un personnage (c)\n"
                       "- Ajouter un personnage (a)\n"
                       "- Voir un personnage (v)\n"
                       "- Donner un personnage (d)\n"
                       "- Modifier un personnage (m)\n"
                       "- Supprimer un personnage (s)\n"
                       "- Liste des personnages (p)\n"
                       "- Voir les roles (r)\n"
                       "- Jouer (j)\n"
                       "- Quitter (q)\n")
        if choice == 'c':
            test = search_char(active_player, input("Quel est le nom du personnage que vous voulez jouer ? "))
            if test:
                character_played = test
            else:
                print("Ce personnage n'existe pas ou ne vous appartient pas")
        if choice == 'a':
            add_char(active_player)
        if choice == 'v':
            fiche_char(active_player,
                       search_char(active_player, input("Quel est le nom du personnage que vous voulez voir ? ")))
        if choice == 'd':
            donate_char(active_player,
                        input("Quel est le nom du joueur à qui vous voulez donner un personnage ? "),
                        search_char(active_player, input("Quel est le nom du personnage que vous voulez donner ? ")))
        if choice == 'm':
            modify_char(active_player, search_char(active_player, input(
                "Quel est le nom du personnage que vous voulez modifier ? ")))
        if choice == 's':
            char_to_delete = search_char(active_player,
                                         input("Quel est le nom du personnage que vous voulez supprimer ? "))
            if char_to_delete == character_played:
                character_played = default_char
            if fiche_char(active_player, char_to_delete):
                choice = input("Etes vous sur de vouloir le supprimer (o/n) ? ")
                if choice == 'o':
                    delete_char(active_player, char_to_delete)
        if choice == 'p':
            list_char(active_player)
        if choice == 'r':
            list_roles(active_player)
        if choice == 'j' and character_played != default_char:
            run(character_played)


def run(character: Character):
    print(f"Jouons, {character.name}")


def make_choice() -> str:
    if active_player == default_player:
        return input("-----------MENU-----------\n"
                     "- Connecter un compte (c)\n"
                     "- Créer un nouveau compte (n)\n"
                     "- Liste des joueurs (l)\n"
                     "- Jouer (j)\n"
                     "- Quitter (q)\n")
    else:
        return input(f"[{active_player.name}]\n"
                     "-----------MENU-----------\n"
                     "- Modifier votre compte (m)\n"
                     "- Supprimer votre compte (s)\n"
                     "- Jouer (j)\n"
                     "- Se déconnecter (d)\n"
                     "- Quitter (q)\n")


def bad_choice():
    print("Commande non reconnue\n")


def false() -> bool:
    print("A la prochaine!")
    return False


def menu(choice):
    return {
       'c': connect_player,
       'n': create_player,
       'm': modify_player,
       's': delete_player,
       'l': list_players,
       'j': char,
       'd': logout,
       'q': false,
    }.get(choice, bad_choice)()


if __name__ == '__main__':
    fetch()
    while is_running:
        if menu(make_choice()) is False:
            is_running = False
