import json
from Database import *
from Player import *
from Personnage import *
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

is_running = True
dead_player = Player(0, "dead", 0)
default_player = Player(0, "default", 0)
active_player = default_player
default_role = Role(0, "default", 0, 0, 0, 0)
default_perso = Personnage(0, active_player, "default", 'M', 0, default_role)
personnage_played = default_perso
players = []
personnages = []
roles = []


def fetch():
    try:
        for dbrole in database.select("role", ["id", "label", "pv", "pa", "pm", "mana"]):
            roles.append(Role(dbrole[0], dbrole[1], dbrole[2], dbrole[3], dbrole[4], dbrole[5]))
        for dbuser in database.select("player", ["id", "name", "age"]):
            players.append(Player(dbuser[0], dbuser[1], dbuser[2]))
        for dbperso in database.select("personnage", ["id", "name", "sexe", "age", "role_id", "player_id", "pv", "pa", "pm", "mana"]):
            role_id = dbperso[4]
            _role = default_role
            if role_id:
                for role in roles:
                    if role.id == role_id:
                        _role = role
            user = dead_player
            player_id = dbperso[5]
            if player_id:
                for player in players:
                    if player.id == player_id:
                        user = player
            personnage = Personnage(dbperso[0], user, dbperso[1], dbperso[2], dbperso[3], _role)
            personnage.pv = dbperso[6]
            personnage.pa = dbperso[7]
            personnage.pm = dbperso[8]
            personnage.mana = dbperso[9]
            personnages.append(personnage)
            _role.personnages.append(personnage)
            user.personnages.append(personnage)
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


def test_player(name: str) -> Player:
    for all_player in players:
        if all_player.name == name:
            return all_player


def create_player() -> Player:
    name = input("Quel es ton nom ? ")
    if test_player(name):
        print("Ce nom est déjà prit\n")
        return default_player
    new_id = len(players) + 1
    age = int(input("Quel age as-tu? "))
    player = Player(new_id, name, age)
    players.append(player)
    database.insert_one("player", ["id", "name", "age"], (new_id, name, age))
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


def delete_player() -> Player:
    logout()
    if not test_player(active_player.name):
        print("Ce joueur n'existe pas\n")
        return default_player
    choice = input("\nEtes vous sur de vouloir le supprimer (o/n) ? \n")
    if choice == 'o':
        for perso in active_player.personnages:
            delete_perso(active_player, perso)
        players.remove(active_player)
        database.delete_by("player", "id = %s", (active_player.id,))
        print("Joueur supprimé\n")
        return active_player


def connect_player() -> Player:
    global active_player
    name = input("Quel est votre nom ? ")
    test = test_player(name)
    if not test:
        print("Ce compte n'existe pas\n")
        return default_player
    active_player = test
    print(f"\nBonjour {active_player.name} !")
    return active_player


def logout():
    global active_player
    global personnage_played
    active_player = default_player
    personnage_played = default_perso
    print("Au revoir !")


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
        persos = []
        for perso in player.personnages:
            if perso.role == role:
                persos.append(perso)
        to_print = "Personnages : "
        if not persos:
            to_print += "Aucun"
        to_print += persos[0].name
        for index in range(1, len(persos)):
            to_print += f", {persos[index].name}"
        print(to_print)


# CRUD Personnages
def list_perso(player: Player):
    if not player.personnages:
        print("\nAucun personnage")
        return
    print("Liste de vos personnages :")
    for perso in player.personnages:
        if perso.player == player:
            print(f"-> {perso.name}")


def test_perso(player: Player, personnage: Personnage) -> Personnage:
    if not personnage or personnage not in personnages:
        return default_perso
    if personnage.player == player:
        if personnage in player.personnages:
            return personnage


def search_perso(player: Player, name: str) -> Personnage:
    for perso in player.personnages:
        if perso.name == name:
            return perso


def fiche_perso(player: Player, personnage: Personnage) -> Personnage:
    if not test_perso(player, personnage):
        print("Personnage non existant ou non possédé")
        return default_perso
    sexe = "Aucun"
    if personnage.sexe == 'H':
        sexe = "Homme"
    if personnage.sexe == 'F':
        sexe = "Femme"
    print(
        f"Fiche perso\n"
        f"- Nom : {personnage.name}\n"
        f"- Sexe : {sexe}\n"
        f"- Age : {personnage.age} ans\n"
        f"- Role : {personnage.role.label}\n"
        f"PV={personnage.pv} PA={personnage.pa} PM={personnage.pm} Mana={personnage.mana}\n"
    )
    return personnage


def add_perso(player: Player) -> Personnage:
    name = input("Quel est le nom de votre personnage ? ")
    if search_perso(player, name):
        print("Ce nom est déjà prit\n")
        return default_perso
    role = search_role(input("Quel est le role de ton personnage ? "))
    if not role:
        print("Ce role n'existe pas\n")
        return default_perso
    sexe = input("Votre personnage est-il un homme ou une femme (H/F) ? ")
    if sexe != 'H' and sexe != 'F':
        print("Veuillez bien respecter la syntaxe demandée (H/F)\n")
        return default_perso
    age = int(input("Quel est l'age de votre personnage ? "))
    perso = Personnage(len(personnages) + 1, player, name, sexe, age, role)
    personnages.append(perso)
    player.personnages.append(perso)
    role.personnages.append(perso)
    if not active_player == default_player:
        database.insert_one(
            "personnage",
            ["id", "player_id", "role_id", "name", "sexe", "age", "pv", "pa", "pm", "mana"],
            (
                len(personnages) + 1, player.id, role.id, name, sexe, age, role.pv, role.pa, role.pm,
                role.mana)
            )
    print("Personnage créé")
    return perso


def modify_perso(player: Player, personnage: Personnage):
    if fiche_perso(player, personnage):
        choice = -1
        while choice != 'b':
            choice = input("\nMODIFIER LE PERSONNAGE\n"
                           "- Modifier le nom (n)\n"
                           "- Modifier le sexe (s)\n"
                           "- Modifier l'age (a)\n"
                           "- Retour (b)\n")
            if choice == 'n':
                name = input("Quel est son nom ? ")
                personnage.name = name
                if not player == default_player:
                    database.update_one("personnage", ["name"], f"id = %s", (name, personnage.id))
            if choice == 's':
                sexe = input("Quel est son sexe (H/F) ? ")
                if sexe == 'H' or sexe == 'F':
                    personnage.sexe = sexe
                    if not player == default_player:
                        database.update_one("personnage", ["sexe"], f"id = %s", (sexe, personnage.id))
                else:
                    print("Veuillez bien respecter la syntaxe demandée (H/F)\n")
            if choice == 'a':
                age = int(input("Quel est son age ? "))
                personnage.age = age
                if not player == default_player:
                    database.update_one("personnage", ["age"], f"id = %s", (age, personnage.id))


def delete_perso(player: Player, personnage: Personnage) -> Personnage:
    if not test_perso(player, personnage):
        print("Personnage introuvable")
        return default_perso
    personnages.remove(personnage)
    player.personnages.remove(personnage)
    personnage.player = dead_player
    if not player == default_player:
        database.delete_by("personnage", "id = %s", (personnage.id,))
    print("Personnage supprimé\n")
    return personnage


def donate_perso(p_origin: Player, p_target: Player, personnage: Personnage) -> Personnage:
    if not test_player(p_origin.name) or p_origin == default_player:
        print("Le joueur donateur n'existe pas")
        return default_perso
    p_target = test_player(p_target)
    if not p_target or p_target == default_player:
        print("Le joueur cible n'existe pas")
        return default_perso
    if personnage == default_perso or personnage not in p_origin.personnages:
        print("Ce personnage ne vous appartient pas")
        return default_perso
    p_origin.personnages.remove(personnage)
    personnage.player = dead_player
    p_target.personnages.append(personnage)
    personnage.player = p_target
    database.update_one("personnage", ["player_id"], f"id = %s", (p_target.id, personnage.id))
    print("Personnage donné avec succès")
    return personnage


def perso():
    global personnage_played
    choice = -1
    while choice != 'q':
        if personnage_played == default_perso:
            print("\nVeuillez choisir un personnage pour jouer")
        else:
            print(f"\nVous avez choisi {personnage_played.name}")
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
            test = search_perso(active_player, input("Quel est le nom du personnage que vous voulez jouer ? "))
            if test:
                personnage_played = test
            else:
                print("Ce personnage n'existe pas ou ne vous appartient pas")
        if choice == 'a':
            add_perso(active_player)
        if choice == 'v':
            fiche_perso(active_player,
                        search_perso(active_player, input("Quel est le nom du personnage que vous voulez voir ? ")))
        if choice == 'd':
            donate_perso(active_player, input("Quel est le nom du joueur à qui vous voulez donner un personnage ? "),
                         search_perso(active_player, input("Quel est le nom du personnage que vous voulez donner ? ")))
        if choice == 'm':
            modify_perso(active_player, search_perso(active_player, input(
                "Quel est le nom du personnage que vous voulez modifier ? ")))
        if choice == 's':
            perso = search_perso(active_player, input("Quel est le nom du personnage que vous voulez supprimer ? "))
            if perso == personnage_played:
                personnage_played = default_perso
            if fiche_perso(active_player, perso):
                choice = input("Etes vous sur de vouloir le supprimer (o/n) ? ")
                if choice == 'o':
                    delete_perso(active_player, perso)
        if choice == 'p':
            list_perso(active_player)
        if choice == 'r':
            list_roles(active_player)
        if choice == 'j' and personnage_played != default_perso:
            run(personnage_played)


def run(personnage: Personnage):
    print(f"Jouons, {personnage.name}")


def make_choice() -> str:
    if active_player == default_player:
        return input("-----------MENU-----------\n"
                     "- Connecter un compte (c)\n"
                     "- Créer un nouveau compte (n)\n"
                     "- Liste des joueurs (l)\n"
                     "- Jouer (j)\n"
                     "- Quitter (q)\n")
    else:
        return input("-----------MENU-----------\n"
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
       'j': perso,
       'd': logout,
       'q': false,
    }.get(choice, bad_choice)()


if __name__ == '__main__':
    fetch()
    while is_running:
        if menu(make_choice()) is False:
            is_running = False
