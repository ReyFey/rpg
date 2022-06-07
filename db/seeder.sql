drop database if exists rpg;
create database if not exists rpg;
use rpg;

create table if not exists player
(
    id   int auto_increment
        primary key,
    name varchar(64) not null,
    age  int         null,
    constraint player_id_uindex
        unique (id)
);

create table if not exists role
(
    id    int auto_increment
        primary key,
    label varchar(64) not null,
    pv    int         null,
    pa    int         null,
    pm    int         null,
    mana  int         null,
    constraint role_id_uindex
        unique (id)
);

create table if not exists `character`
(
    id        int auto_increment
        primary key,
    player_id int         not null,
    role_id   int         not null,
    name      varchar(64) not null,
    sexe      char        null,
    age       int         null,
    pv        int         null,
    pa        int         null,
    pm        int         null,
    mana      int         null,
    constraint character_id_uindex
        unique (id),
    constraint character_player_id_fk
        foreign key (player_id) references player (id),
    constraint character_role_id_fk
        foreign key (role_id) references role (id)
);


