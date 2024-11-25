DROP TABLE IF EXISTS team_references;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS competitive_pokemon;
DROP TABLE IF EXISTS detailed_moves;
DROP TABLE IF EXISTS pokemon;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS types;
DROP TABLE IF EXISTS natures;
DROP TABLE IF EXISTS abilities;
DROP TABLE IF EXISTS egg_groups;
DROP TABLE IF EXISTS held_items;
DROP TABLE IF EXISTS regulations;

DROP TYPE IF EXISTS nature_stat;
DROP TYPE IF EXISTS move_category;
DROP TYPE IF EXISTS move_targets;

CREATE TABLE regions (
	id serial primary key,
	name varchar(255) UNIQUE not null
);

CREATE TABLE types (
	id serial primary key,
	name varchar(255) UNIQUE not null
);

CREATE TYPE nature_stat as ENUM ('Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed');

CREATE TABLE natures (
	id serial primary key,
	name varchar(255) UNIQUE not null,
	boosting_stat nature_stat not null,
	decreasing_stat nature_stat not null
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
	speed smallint not null,
	unique(name,variant,region_id)
);

CREATE TABLE held_items (
	id serial primary key,
	name varchar(255) UNIQUE not null
);

CREATE TYPE move_category as ENUM ('Physical', 'Special', 'Status');
CREATE TYPE move_targets as ENUM ('Single', 'Self', 'Opponents',  'Self or Ally', 'Ally and Opponents', 'Opponent', 'All', 'Party', 'Team', 'Ally', 'Field - Team', 'Field - Opponents', 'Field');

CREATE TABLE detailed_moves (
	id serial primary key,
	name varchar(255) UNIQUE not null,
	type integer references types on delete cascade not null,
	category move_category not null,
	targets move_targets not null,
	pp integer not null,
	hits integer,
	power integer,
	accuracy integer,
	priority integer not null,
	contact boolean not null,
	special_categories jsonb,
	bulbapedia_link varchar not null,
	additional_effects jsonb,
	unimplemented boolean

	CONSTRAINT pp_positive_integer CHECK (pp > 0),
	CONSTRAINT pp_less_than_equal_to_forty CHECK (pp <= 40),
	CONSTRAINT hits_positive_integer CHECK (hits > 0),
	CONSTRAINT hits_less_than_equal_to_ten CHECK (hits <= 10),
	CONSTRAINT power_positive_integer CHECK (power > 0),
	CONSTRAINT power_less_than_equal_to_two_hundred_fifty CHECK (power <= 250),
	CONSTRAINT accuracy_positive_integer CHECK (accuracy > 0),
	CONSTRAINT accuracy_less_than_equal_to_one_hundred CHECK (accuracy <= 100),
	CONSTRAINT priority_greater_than_equal_to_negative_seven CHECK (priority >= -7),
	CONSTRAINT priority_less_than_equal_to_five CHECK (priority <= 5)
);

CREATE TABLE regulations (
	id serial primary key,
	name varchar(1) UNIQUE not null
);

CREATE TABLE competitive_pokemon (
	id serial primary key,
	pokemon_id integer references pokemon on delete cascade not null,
	ability_id integer references abilities on delete cascade not null,
	held_item_id integer references held_items on delete cascade,
	tera_type_id integer references types on delete cascade not null,
	attack_iv smallint CHECK (attack_iv >= 0 and attack_iv <= 31) not null,
	special_attack_iv smallint CHECK (special_attack_iv >= 0 and special_attack_iv <= 31) not null,
	speed_iv smallint CHECK (speed_iv >= 0 and speed_iv <= 31) not null,
	nature_id integer references natures on delete cascade not null,
	hp_evs smallint CHECK (hp_evs >= 0 and hp_evs <= 252) not null,
	attack_evs smallint CHECK (attack_evs >= 0 and attack_evs <= 252) not null,
	defense_evs smallint CHECK (defense_evs >= 0 and defense_evs <= 252) not null,
	special_attack_evs smallint CHECK (special_attack_evs >= 0 and special_attack_evs <= 252) not null,
	special_defense_evs smallint CHECK (special_defense_evs >= 0 and special_defense_evs <= 252) not null,
	speed_evs smallint CHECK (speed_evs >= 0 and speed_evs <= 252) not null,
	move_1_id integer references detailed_moves on delete cascade not null,
	move_2_id integer references detailed_moves on delete cascade,
	move_3_id integer references detailed_moves on delete cascade,
	move_4_id integer references detailed_moves on delete cascade,

	CONSTRAINT valid_evs CHECK ((hp_evs + attack_evs + defense_evs + special_attack_evs + special_defense_evs + speed_evs) <= 510),
	unique(pokemon_id,ability_id,held_item_id,tera_type_id,attack_iv,special_attack_iv,speed_iv,nature_id,hp_evs,attack_evs,defense_evs,special_attack_evs,special_defense_evs,speed_evs,move_1_id,move_2_id,move_3_id,move_4_id)
);

CREATE TABLE teams (
	id serial primary key,
	regulation_id integer references regulations on delete cascade not null,
	competitive_pokemon_1_id integer references competitive_pokemon on delete cascade not null,
	competitive_pokemon_2_id integer references competitive_pokemon on delete cascade not null,
	competitive_pokemon_3_id integer references competitive_pokemon on delete cascade not null,
	competitive_pokemon_4_id integer references competitive_pokemon on delete cascade not null,
	competitive_pokemon_5_id integer references competitive_pokemon on delete cascade not null,
	competitive_pokemon_6_id integer references competitive_pokemon on delete cascade not null,
	paste_url varchar(255) UNIQUE
);

CREATE TABLE team_references (
	id serial primary key,
	team_id integer references teams on delete cascade not null,
	reference varchar(255) not null,
	unique(team_id,reference)
);