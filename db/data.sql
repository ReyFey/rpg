INSERT INTO rpg.player (id, name, age) VALUES (1, 'Victor', 20);
INSERT INTO rpg.player (id, name, age) VALUES (2, 'Louis', 10);

INSERT INTO rpg.role (id, label, pv, pa, pm, mana) VALUES (1, 'mage', 50, 30, 60, 120);
INSERT INTO rpg.role (id, label, pv, pa, pm, mana) VALUES (2, 'assassin', 60, 80, 100, 10);
INSERT INTO rpg.role (id, label, pv, pa, pm, mana) VALUES (3, 'guerrier', 70, 50, 30, 20);
INSERT INTO rpg.role (id, label, pv, pa, pm, mana) VALUES (4, 'voleur', 40, 70, 100, 10);
INSERT INTO rpg.role (id, label, pv, pa, pm, mana) VALUES (5, 'tank', 150, 30, 10, 0);
INSERT INTO rpg.role (id, label, pv, pa, pm, mana) VALUES (6, 'healer', 30, 10, 60, 100);

INSERT INTO rpg.personnage (id, player_id, role_id, name, sexe, age) VALUES (1, 1, 1, 'Reyks', 'H', 30);
INSERT INTO rpg.personnage (id, player_id, role_id, name, sexe, age) VALUES (2, 2, 2, 'Meliodas', 'H', 16);

