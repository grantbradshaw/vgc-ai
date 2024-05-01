DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS types;
DROP TABLE IF EXISTS natures;
DROP TABLE IF EXISTS abilities;
DROP TABLE IF EXISTS egg_groups;
DROP TABLE IF EXISTS pokemon;
DROP TABLE IF EXISTS held_items;
DROP TABLE IF EXISTS moves;
DROP TABLE IF EXISTS regulations;

CREATE TABLE regions (
	id serial primary key,
	name varchar(255) UNIQUE not null
);

CREATE TABLE types (
	id serial primary key,
	name varchar(255) UNIQUE not null
);

CREATE TABLE natures (
	id serial primary key,
	name varchar(255) UNIQUE not null
);

CREATE TABLE abilities (
	id serial primary key,
	name varchar(255) UNIQUE not null
);

CREATE TABLE egg_groups (
	id serial primary key,
	name varchar(255) UNIQUE not null
);

CREATE TABLE pokemon (
	id serial primary key,
	name varchar(255) not null,
	region_id integer references regions on delete cascade not null,
	variant varchar(255),
	national_dex_number smallint not null,
	type_1_id integer references types on delete cascade not null ,
	type_2_id integer references types on delete cascade,
	ability_1_id integer references abilities on delete cascade not null ,
	ability_2_id integer references abilities on delete cascade,
	hidden_ability_id integer references abilities on delete cascade,
	egg_group_1_id integer references egg_groups on delete cascade not null ,
	egg_group_2_id integer references egg_groups on delete cascade,
	weight_kg numeric(4,1) not null,
	hp smallint not null,
	attack smallint not null,
	defense smallint not null,
	special_attack smallint not null,
	special_defense smallint not null,
	speed smallint not null

	unique(national_dex_number,variant,region_id)
);

CREATE TABLE held_items (
	id serial primary key,
	name varchar(255) UNIQUE not null
);

CREATE TABLE moves (
	id serial primary key,
	name varchar(255) UNIQUE not null,
);

CREATE TABLE regulations (
	id serial primary key,
	name varchar(255) UNIQUE not null
);










