DROP TABLE IF EXISTS competitive_pokemon_lookup;

/*
competitive_pokemon_lookup is a table to be a list of all recorded Pokemon with fully known spreads
the intended use is to aid with a baseline for a spread when adding a Pokemon to a team
*/
CREATE TABLE competitive_pokemon_lookup (
	name varchar(255) not null,
	region varchar(255) not null,
	variant varchar(255),
	ability varchar(255) not null,
	held_item varchar(255),
	tera_type varchar(255) not null,
	nature varchar(255) not null,
	regulation varchar(255), -- not null because of "theory pokemon", theorized spreads that are not associated with a competitive team
	ivs jsonb not null,
	evs jsonb not null,
	moves jsonb not null
);