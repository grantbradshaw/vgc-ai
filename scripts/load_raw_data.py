import csv
import json
import numpy as np
import pandas as pd
from sqlalchemy import text

from helpers.establish_db_connection import get_db_engine
from helpers.utility import get_fk_id, insert_row

# load_data is always destructive, as the data being loaded here should never be updated directly in the database. 
def initialize_data():
	engine = get_db_engine()
	with engine.connect() as conn:

		conn.execute(text("DELETE FROM regions"))
		conn.execute(text("ALTER SEQUENCE regions_id_seq RESTART WITH 1"))
		with open("data/regions.json") as region_infile:
			regions = json.load(region_infile)
			for region in regions:
				conn.execute(text("INSERT INTO regions (name) VALUES ('{}')".format(region)))

		conn.execute(text("DELETE FROM types"))
		conn.execute(text("ALTER SEQUENCE types_id_seq RESTART WITH 1"))
		with open("data/types.json") as type_infile:
			types = json.load(type_infile)
			for poke_type in types:
				conn.execute(text("INSERT INTO types (name) VALUES ('{}')".format(poke_type)))

		conn.execute(text("DELETE FROM natures"))
		conn.execute(text("ALTER SEQUENCE natures_id_seq RESTART WITH 1"))
		with open("data/natures.json") as nature_infile:
			natures = json.load(nature_infile)
			for nature in natures:
				conn.execute(text("INSERT INTO natures (name, boosting_stat, decreasing_stat) VALUES ('{}')".format("','".join([nature, natures[nature]["Boosts"], natures[nature]["Decreases"]]))))

		conn.execute(text("DELETE FROM abilities"))
		conn.execute(text("ALTER SEQUENCE abilities_id_seq RESTART WITH 1"))
		with open("data/abilities.json") as ability_infile:
			abilities = json.load(ability_infile)
			# As the plain text json contains single quotations, they must be reformatted appropriately for Postgres
			for ability in abilities:
				conn.execute(text("INSERT INTO abilities (name) VALUES ('{}')".format(ability.replace("'", "''"))))

		conn.execute(text("DELETE FROM egg_groups"))
		conn.execute(text("ALTER SEQUENCE egg_groups_id_seq RESTART WITH 1"))
		with open("data/egg_groups.json") as egg_group_infile:
			egg_groups = json.load(egg_group_infile)
			for egg_group in egg_groups:
				conn.execute(text("INSERT INTO egg_groups (name) VALUES ('{}')".format(egg_group)))

		conn.execute(text("DELETE FROM held_items"))
		conn.execute(text("ALTER SEQUENCE held_items_id_seq RESTART WITH 1"))
		with open("data/held_items.json") as held_items_infile:
			held_items = json.load(held_items_infile)
			for held_item in held_items:
				conn.execute(text("INSERT INTO held_items (name) VALUES ('{}')".format(held_item.replace("'", "''"))))

		conn.execute(text("DELETE FROM detailed_moves"))
		conn.execute(text("ALTER SEQUENCE detailed_moves_id_seq RESTART WITH 1"))
		with open("data/detailed_moves.csv") as detailed_moves_infile:
			detailed_moves_reader = csv.reader(detailed_moves_infile)
			move_effects = json.load(open("data/move_effects.json"))
			unimplemented_moves = json.load(open("data/unimplemented_moves.json"))

			detailed_moves_row_count = 0
			for row in detailed_moves_reader:
				detailed_moves_row_count += 1
				if detailed_moves_row_count > 1:
					detailed_moves_insert = {"name": row[0].replace("'", "''"),
											 "type": get_fk_id("types", row[1], conn_arg=conn),
											 "category": row[2],
											 "targets": row[3],
											 "pp": row[4],
											 "hits": row[5],
											 "power": row[6],
											 "accuracy": row[7],
											 "priority": row[8],
											 "contact": row[9],
											 "bulbapedia_link": row[11]
										    }
					if len(row[10]) > 0:
						detailed_moves_insert["special_categories"] = json.dumps(list(map(lambda x: x.strip(), row[10].split(","))))
					if row[0] in move_effects:
						detailed_moves_insert["additional_effects"] = json.dumps(move_effects[row[0]])
					if row[0] in unimplemented_moves:
						detailed_moves_insert["unimplemented"] = True
					insert_row(detailed_moves_insert, "detailed_moves", conn)

		conn.execute(text("DELETE FROM regulations"))
		conn.execute(text("ALTER SEQUENCE regulations_id_seq RESTART WITH 1"))
		with open("data/regulations.json") as regulations_infile:
			regulations = json.load(regulations_infile)
			for regulation in regulations:
				conn.execute(text("INSERT INTO regulations (name) VALUES ('{}')".format(regulation)))

		conn.execute(text("DELETE FROM pokemon"))
		conn.execute(text("ALTER SEQUENCE pokemon_id_seq RESTART WITH 1"))

		pokemon_df = pd.read_csv("data/pokemon.csv")
		# allow_none is only set to True if it is possible for this value to be null for a Pokemon
		# put differently, it is assumed that data/pokemon.csv is formatted properly, and error handling will happen gracelessly in get_fk_id
		pokemon_df["region_id"] = pokemon_df["Original Region"].apply(lambda x: get_fk_id("regions", x, conn_arg=conn))
		pokemon_df["type_1_id"] = pokemon_df["Type 1"].apply(lambda x: get_fk_id("types", x, conn_arg=conn))
		pokemon_df["type_2_id"] = pokemon_df["Type 2"].apply(lambda x: get_fk_id("types", x, conn_arg=conn, allow_none=True))
		pokemon_df["ability_1_id"] = pokemon_df["Ability 1"].apply(lambda x: get_fk_id("abilities", x, conn_arg=conn))
		pokemon_df["ability_2_id"] = pokemon_df["Ability 2"].apply(lambda x: get_fk_id("abilities", x, conn_arg=conn, allow_none=True))
		pokemon_df["hidden_ability_id"] = pokemon_df["Hidden Ability"].apply(lambda x: get_fk_id("abilities", x, conn_arg=conn, allow_none=True))
		pokemon_df["egg_group_1_id"] = pokemon_df["Egg Group 1"].apply(lambda x: get_fk_id("egg_groups", x, conn_arg=conn))
		pokemon_df["egg_group_2_id"] = pokemon_df["Egg Group 2"].apply(lambda x: get_fk_id("egg_groups", x, conn_arg=conn, allow_none=True))

		# finally, we remap our DataFrame columns to align with our DB columns
		pokemon_df = pokemon_df.rename(columns={
											   "Name": "name", 
											   "Variant": "variant",
											   "National Dex #": "national_dex_number",
											   "Weight (kg)": "weight_kg",
											   "HP": "hp",
											   "Atk": "attack",
											   "Def": "defense",
											   "Sp. Atk": "special_attack",
											   "Sp. Def": "special_defense",
											   "Speed": "speed"
								   			   })

		pokemon_df.apply(lambda x: insert_series(x, conn), axis=1)
		
		conn.commit()

def insert_series(s, conn):
	insert = {
		"name": s["name"],
		"region_id": s["region_id"],
		"national_dex_number": s["national_dex_number"],
		"type_1_id": s["type_1_id"],
		"ability_1_id": s["ability_1_id"],
		"egg_group_1_id": s["egg_group_1_id"],
		"weight_kg": s["weight_kg"],
		"hp": s["hp"],
		"attack": s["attack"],
		"defense": s["defense"],
		"special_attack": s["special_attack"],
		"special_defense": s["special_defense"],
		"speed": s["speed"]
	}

	if not pd.isnull(s["variant"]):
		insert["variant"] = s["variant"]
	if not pd.isnull(s["type_2_id"]):
		insert["type_2_id"] = int(s["type_2_id"])
	if not pd.isnull(s["ability_2_id"]):
		insert["ability_2_id"] = int(s["ability_2_id"])
	if not pd.isnull(s["hidden_ability_id"]):
		insert["hidden_ability_id"] = int(s["hidden_ability_id"])
	if not pd.isnull(s["egg_group_2_id"]):
		insert["egg_group_2_id"] = int(s["egg_group_2_id"])

	insert_row(insert, "pokemon", conn)


initialize_data()
