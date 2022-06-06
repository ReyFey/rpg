from Database import *
from Player import *
from Personnage import *
from Role import *

try:
    database = Database('localhost', '3306', 'dev', '', 'rpg')
except:
    print("Impossible de se connecter à la base de données\n")
finally:
    print("Base de données connectée\n")

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
        for dbrole in database.select("SELECT id, label, pv, pa, pm, mana FROM rpg.role"):
            roles.append(Role(dbrole[0], dbrole[1], dbrole[2], dbrole[3], dbrole[4], dbrole[5]))
        for dbuser in database.select("SELECT id, name, age FROM rpg.player"):
            players.append(Player(dbuser[0], dbuser[1], dbuser[2]))
        for dbperso in database.select("SELECT id, name, sexe, age, role_id, player_id FROM rpg.personnage"):
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
            personnages.append(personnage)
            _role.personnages.append(personnage)
            user.personnages.append(personnage)
    except:
        print("Les données n'ont pas pu se charger correctement\n")
    finally:
        print("Les données sont chargées\n")


# CRUD Players
def list_players():
    if not players:
        print("\nAucun joueur\n")
        return

    for player in players:
        print(f"-> {player.name}")
    print("")


def test_player(name):
    for all_player in players:
        if all_player.name == name:
            return all_player
            break


def create_player():
    name = input("Quel es ton nom ? ")
    if not test_player(name):
        new_id = len(players) + 1
        age = int(input("Quel age as-tu? "))
        player = Player(new_id, name, age)
        players.append(player)
        database.insert_one("player", ["id", "name", "age"], (new_id, name, age))
        print("Joueur créé\n")
        return player
    else:
        print("Ce nom est déjà prit\n")


def modify_player(player):
    choice = -1
    while choice != 'q':
        choice = input("\nMODIFIER LE COMPTE\n"
                 f"{player.name}, {player.age} ans\n"
                 "- Modifier le nom (n)\n"
                 "- Modifier l'age (a)\n"
                 "- Quitter (q)\n")
        if choice == 'n':
            name = input("Quel est votre nom ? ")
            player.name = name
            database.update("player", ["name"], f"id = %s", (name, player.id))
        if choice == 'a':
            age = int(input("Quel est votre age ? "))
            player.age = age
            database.update("player", ["age"], f"id = %s", (age, player.id))


def delete_player(player):
    logout()
    if not test_player(player.name):
        print("Ce joueur n'existe pas\n")
        return
    choice = input("\nEtes vous sur de vouloir le supprimer (o/n) ? \n")
    if choice == 'o':
        for perso in player.personnages:
            delete_perso(player, perso)
        players.remove(player)
        database.delete_by("player", "id = %s", (player.id,))
        print("Joueur supprimé\n")
        return player


def connect_player():
    global active_player
    name = input("Quel est votre nom ? ")
    test = test_player(name)
    if not test:
        print("Ce compte n'existe pas\n")
        return
    else:
        active_player = test
        print(f"\nBonjour {active_player.name} !")
        return active_player


def logout():
    global active_player
    global personnage_played
    active_player = default_player
    personnage_played = default_perso
    print("Au revoir !")


# CRUD Persos
def list_perso(player):
    if not player.personnages:
        print("\nAucun personnage")
        return
    for perso in player.personnages:
        if perso.player == player:
            print(f"-> {perso.name}")


def test_perso(player, personnage):
    if not personnage or personnage not in personnages:
        return
    if personnage.player == player:
        if personnage in player.personnages:
            return personnage


def search_perso(player, name):
    for perso in player.personnages:
        if perso.name == name:
            return perso


# Gestion des roles
def search_role(name):
    for role in roles:
        if role.label == name:
            return role


def list_roles(player):
    if not roles:
        print("\nAucun role\n")
        return
    for role in roles:
        print(f"\n~~~{role.label.upper()}~~~\n"
            f"{role.PV} points de vie (PV)\n"
            f"{role.PA} points d'attaque (PA)\n"
            f"{role.PM} points de mouvement (PM)\n"
            f"{role.mana} points de magie (Mana)")
        persos = []
        for perso in player.personnages:
            if perso.role == role:
                persos.append(perso)
        to_print = "Personnages : "
        if persos:
            to_print += persos[0].name
            for index in range(1, len(persos)):
                to_print += f", {persos[index].name}"
        else:
            to_print += "Aucun"
        print(to_print)


def fiche_perso(player, personnage):
    if not test_perso(player, personnage):
        print("Personnage non existant ou non possédé")
    else:
        sexe = "aucun"
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
            f"PV={personnage.role.PV} PA={personnage.role.PA} PM={personnage.role.PM} Mana={personnage.role.mana}\n"
        )
        return personnage


def add_perso(player):
    name = input("Quel est le nom de votre personnage ? ")
    role = search_role(input("Quel est le role de ton personnage ? "))
    if not search_perso(player, name):
        if role:
            sexe = input("Votre personnage est-il un homme ou une femme (H/F) ? ")
            if sexe == 'H' or sexe == 'F':
                age = int(input("Quel est l'age de votre personnage ? "))
                perso = Personnage(len(personnages)+1, player, name, sexe, age, role)
                player.personnages.append(perso)
                role.personnages.append(perso)
                database.insert_one(
                    "personnage",
                    ["id", "player_id", "role_id", "name", "sexe", "age"],
                    (len(personnages)+1, player.id, role.id, name, sexe, age)
                )
                print("Personnage créé")
                return perso
            else:
                print("Veuillez bien respecter la syntaxe demandée (H/F)\n")
        else:
            print("Ce role n'existe pas\n")
    else:
        print("Ce nom est déjà prit\n")


def modify_perso(player, personnage):
    fiche_perso(player, personnage)
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
            database.update("personnage", ["name"], f"id = %s", (name, personnage.id))
        if choice == 's':
            sexe = input("Quel est son sexe (H/F) ? ")
            if sexe == 'H' or sexe == 'F':
                personnage.sexe = sexe
                database.update("personnage", ["sexe"], f"id = %s", (sexe, personnage.id))
            else:
                print("Veuillez bien respecter la syntaxe demandée (H/F)\n")
        if choice == 'a':
            age = int(input("Quel est son age ? "))
            personnage.age = age
            database.update("personnage", ["age"], f"id = %s", (age, personnage.id))


def delete_perso(player, personnage):
    if test_perso(player, personnage):
        player.personnages.remove(personnage)
        personnage.player = dead_player
        database.delete_by("personnage", "id = %s", (personnage.id,))
        print("Personnage supprimé\n")


def perso(player):
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
            fiche_perso(active_player, search_perso(active_player, input("Quel est le nom du personnage que vous voulez voir ? ")))
        if choice == 'm':
            modify_perso(active_player, search_perso(active_player, input("Quel est le nom du personnage que vous voulez modifier ? ")))
        if choice == 's':
            perso = search_perso(active_player, input("Quel est le nom du personnage que vous voulez supprimer ? "))
            if perso == personnage_played:
                personnage_played = default_perso
            fiche_perso(active_player, perso)
            choice = input("Etes vous sur de vouloir le supprimer (o/n) ? ")
            if choice == 'o':
                delete_perso(active_player, perso)
        if choice == 'p':
            list_perso(active_player)
        if choice == 'r':
            list_roles(active_player)
        if choice == 'j' and personnage_played != default_perso:
            run(personnage_played)


def run(perso):
    print(f"Jouons, {perso.name}")


def menu():
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


if __name__ == '__main__':
    fetch()
    while is_running:
        choice = menu()

        if choice == 'c':
            connect_player()

        if choice == 'n':
            create_player()

        if choice == 'm':
            modify_player(active_player)

        if choice == 's':
            delete_player(active_player)

        if choice == 'l':
            list_players()

        if choice == 'j':
            perso(active_player)

        if choice == 'd':
            logout()

        if choice == 'q':
            is_running = False
