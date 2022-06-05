from Player import *
from Personnage import *
from Role import *

is_running = True
dead_player = Player("dead", 0)
default_player = Player("default", 0)
active_player = default_player
roles = [Role("mage", 50, 30, 60, 120), Role("assassin", 60, 80, 100, 10), Role("guerrier", 70, 50, 30, 20), Role("voleur", 40, 70, 100, 10), Role("tank", 150, 30, 10, 0), Role("healer", 30, 10, 60, 100)]
default_perso = Personnage(active_player, "default", 'M', 0, Role("default", 0, 0, 0, 0))
personnage_played = default_perso
players = []


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
        player = Player(name, input("Quel age as-tu? "))
        players.append(player)
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
            player.name = input("Quel est votre nom ? ")
        if choice == 'a':
            player.age = input("Quel est votre age ? ")


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


def delete_player(player):
    logout()
    if not test_player(player.name):
        print("Ce joueur n'existe pas\n")
        return
    choice = input("\nEtes vous sur de vouloir le supprimer (o/n) ? \n")
    if choice == 'o':
        players.remove(player)
        print("Joueur supprimé\n")
        return player


def logout():
    global active_player
    active_player = default_player
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
    if personnage.player == player:
        if personnage in player.personnages:
            return personnage


def search_perso(player, name):
    for perso in player.personnages:
        if perso.name == name:
            return perso


def search_role(name):
    for role in roles:
        if role.label == name:
            return role


def add_role(personnage):
    role = search_role(input("Quel est le role de ton personnage ? "))
    if role:
        personnage.role = role
        role.personnages.append(personnage)
    else:
        print("Ce role n'existe pas\n")


def fiche_perso(player, personnage):
    if not test_perso(player, personnage):
        print("Personnage non existant ou non possédé")
    else:
        print(
            f"Fiche perso\n"
            f"- Nom : {personnage.name}\n"
            f"- Sexe : {personnage.sexe}\n"
            f"- Age : {personnage.age}\n"
            f"- Role : {personnage.role.label}\n"
            f"PV={personnage.role.PV} PA={personnage.role.PA} PM={personnage.role.PM} Mana={personnage.role.mana}\n"
        )
        return personnage


def add_perso(player):
    name = input("Quel est le nom de votre personnage ? ")
    role = search_role(input("Quel est le role de ton personnage ? "))
    if not search_perso(player, name):
        if role:
            perso = Personnage(player, name, input("Votre personnage est-il un homme ou une femme (H/F) ? "), input("Quel est l'age de votre personnage ? "), role)
            player.personnages.append(perso)
            role.personnages.append(perso)
            print("Personnage créé")
            return perso
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
                       "- Modifier le role (r)\n"
                       "- Retour (b)\n")
        if choice == 'n':
            personnage.name = input("Quel est son nom ? ")
        if choice == 's':
            personnage.sexe = input("Quel est son sexe (H/F) ? ")
        if choice == 'a':
            personnage.age = input("Quel est son age ? ")
        if choice == 'r':
            add_role(personnage)


def delete_perso(player, personnage):
    global personnage_played
    if fiche_perso(player, personnage):
        choice = input("Etes vous sur de vouloir le supprimer (o/n) ? ")
        if choice == 'o':
            player.personnages.remove(personnage)
            personnage.player = dead_player
            personnage_played = default_perso
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
            delete_perso(active_player, search_perso(active_player, input("Quel est le nom du personnage que vous voulez supprimer ? ")))
        if choice == 'p':
            list_perso(active_player)
        if choice == 'j':
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
