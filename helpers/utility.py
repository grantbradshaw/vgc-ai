import pandas as pd
from sqlalchemy import text

from helpers.establish_db_connection import get_db_engine

# helper function to get id for simple reference tables
# this function assumes that finding the foreign key is required, and fails if it cannot find a result
def get_fk_id(table, name, conn_arg=None):
	if table not in ["regions", "types", "natures", "abilities", "egg_groups", "held_items", "moves", "regulations"]:
		raise Exception("Table {} does not cohere to an id / name schema.".format(table))

	# if get_fk_id is passed a "null" value, this function simply bounces it back
	# by extension, this function will not search null names
	if name == "" or name == None or pd.isnull(name):
		raise Exception("get_fk_id will not search null values")

	if conn_arg == None:
		engine = get_db_engine()
		conn = engine.connect()
	else:
		conn = conn_arg

	result_df = pd.read_sql("SELECT id from {} where name = '{}'".format(table, name.replace("'", "''")), conn)

	if conn_arg == None:
		conn.close()

	if len(result_df.index) == 0:
		raise Exception("Could not find row in table {} with name {}.".format(table, name))
	elif len(result_df.index) > 1:
		raise Exception("Unexpected duplicate row in table {} for name {}.".format(table, name))
	else:
		fk_id = result_df.at[0, "id"]

	return fk_id

# expects a dictionary of format {"column": "value",...}
# this must be passed a connection - this helper is intended to be run as part of a transaction and does not commit
def insert_row(insert, table, conn):
	if not isinstance(insert, dict):
		raise Exception("insert_row expects a dictionary, but received arg of type {}".format(str(type(insert))))

	columns = []
	values = []

	for key, value in insert.items():
		columns.append(key)
		values.append(str(value))

	conn.execute(text("INSERT INTO {} ({}) VALUES ({})".format(table, ",".join(columns), "'" + "','".join(values) + "'")))

	return True


def get_pokemon_id(name, region_id, variant, conn_arg=None):
	if conn_arg == None:
		engine = get_db_engine()
		conn = engine.connect()
	else:
		conn = conn_arg
	
	# if no region_id is passed, then this is either a pokemon with no regional variants or the first instance of it
	if variant is None and region_id is None:
		query_string = "SELECT id from pokemon where name = '{}' order by region_id asc limit 1".format(name)
	elif variant is None and region_id is not None:
		query_string = "SELECT id from pokemon where name = '{}' and region_id = '{}'".format(name, region_id)
	elif variant is not None and region_id is None:
		query_string = "SELECT id from pokemon where name = '{}' and variant = '{}' order by region_id asc limit 1".format(name, variant)
	elif variant is not None and region_id is not None:
		query_string = "SELECT id from pokemon where name = '{}' and variant = '{}' and region_id = '{}'".format(name, variant, region_id)

	result_df = pd.read_sql(query_string, conn)
	if conn_arg == None:
		conn.close()

	if len(result_df.index) == 1:
		return result_df.at[0, "id"]
	elif len(result_df.index) == 0:
		raise Exception("Could not find pokemon with name = {}, region_id = {}, variant = {}".format(name, region_id, variant))
	else:
		raise Exception("Unexpected ambiguous result for name = {}, region_id = {}, variant = {}".format(name, region_id, variant))

# this function inserts a row for a competitive pokemon if that unique set is not already present in the database
# then returns the id representing this unique competitive pokemon
def insert_competitive_pokemon(conn, pokemon_data):
	if not isinstance(pokemon_data, dict):
		raise Exception("insert_competitive_pokemon expected a dictionary for pokemon_data, but received {}".format(type(pokemon_data)))

	# there are explicitly two validation flows
	# either the pokemon is from an open team sheet (and so has a restricted set of values) or a closed team sheet (and must have everything)

	# nullable means that it could be omitted from a closed team sheet due to not being on the Pokemon in reality
	# required can have three values - all means for any competitive pokemon, cts means only for closed team sheets, never is never
	validate = {
		"pokemon": {"required": "all",
					"type": str},
		"ability": {"required": "all",
					"type": str},
		"tera_type": {"required": "all",
					  "type": str},
		"held_item": {"required": "never",
				 "type": str},
		"moves": {"required": "all",
			      "type": list},
		"nature": {"required": "cts",
				   "type": str},
		"region": {"required": "never",
				   "type": str},
		"variant": {"required": "never",
					"type": str},
		"ivs": {"required": "cts",
				"type": dict},
		"evs": {"required": "cts",
				"type": dict}
	}

	closed_team_sheet = False
	ivs_l = ["attack_iv", "special_attack_iv", "speed_iv"]
	evs_l = ["hp_evs", "attack_evs", "defense_evs", "special_attack_evs", "special_defense_evs", "speed_evs"]

	# if one closed team sheet value is present, we will require all to be
	for key, value in validate.items():
		if value["required"] == "cts" and key in pokemon_data:
			closed_team_sheet = True

	for key, value in validate.items():
		# first, check if the key is present if required
		if value["required"] == "all" and not key in pokemon_data: 
			raise Exception("insert_competitive_pokemon requires key {} to be present, but was not.".format(key))
		elif closed_team_sheet and value["required"] == "cts" and not key in pokemon_data:
			raise Exception("insert_competitive_pokemon requires key {} to be present for this closed team sheet pokemon, but was not.".format(key))

		# next, check if associated value is the proper type and populated properly
		if key in pokemon_data:
			if not isinstance(pokemon_data[key], value["type"]):
				raise Exception("insert_competitive_pokemon requires {} to be type {}, but was {}.".format(key, value["type"], type(pokemon_data[key])))

			if value["type"] == str and len(pokemon_data[key]) == 0:
				raise Exception("insert_competitive_pokemon does not accept empty strings - do not include key {} if null".format(key))

	if len(pokemon_data["moves"]) == 0:
		raise Exception("insert_competitive_pokemon requires at least one move for a Pokemon")
	elif len(pokemon_data["moves"]) > 4:
		raise Exception("insert_competitive_pokemon cannot handle more than 4 moves, but was passed {}".format(len(pokemon_data["moves"])))

	for move in pokemon_data["moves"]:
		if not isinstance(move, str):
			raise Exception("insert_competitive_pokemon expects strings for moves, but received {}".format(type(move)))
		if len(move) == 0:
			raise Exception("insert_competitive_pokemon does not accept empty strings for moves".format(key))


	if "ivs" in pokemon_data:
		for iv in ivs_l:
			if iv not in pokemon_data["ivs"]:
				raise Exception("insert_competitive pokemon requires {} to be in pokemon_data\"[\"ivs\"], but was not.".format(iv))

			if not isinstance(pokemon_data["ivs"][iv], int):
				raise Exception("insert_competitive_pokemon expects an int for iv {}, but received {}".format(iv, type(pokemon_data["ivs"][iv])))

			if pokemon_data["ivs"][iv] < 0 or pokemon_data["ivs"][iv] > 31:
				raise Exception("insert_competitive_pokemon requires ivs to be between 0 and 31, but received {} for iv {}".format(pokemon_data["ivs"][iv], iv))

	if "evs" in pokemon_data:
		for ev in evs_l:
			if ev not in pokemon_data["evs"]:
				raise Exception("insert_competitive pokemon requires {} to be in pokemon_data\"[\"evs\"], but was not.".format(ev))

			if not isinstance(pokemon_data["evs"][ev], int):
				raise Exception("insert_competitive_pokemon expects an int for ev {}, but received {}".format(ie, type(pokemon_data["evs"][ev])))

			if pokemon_data["ivs"][iv] < 0 or pokemon_data["ivs"][iv] > 252:
				raise Exception("insert_competitive_pokemon requires evs to be between 0 and 252, but received {} for ev {}".format(pokemon_data["ivs"][ev], ev))

	ability_id = get_fk_id("abilities", pokemon_data["ability"], conn_arg=conn)
	tera_type_id = get_fk_id("types", pokemon_data["tera_type"], conn_arg=conn)
	move_ids = []
	for move in pokemon_data["moves"]:
		move_id = get_fk_id("moves", move, conn_arg=conn)
		move_ids.append(move_id)

	# as a symptom of our current schema, we must explicitly order moves to ensure 
	# consistency and avoiding failing to match an identical pokemon with differently ordered moves
	move_ids.sort()

	held_item_id = None
	if "held_item" in pokemon_data:
		held_item_id = get_fk_id("held_items", pokemon_data["held_item"], conn_arg=conn)

	region_id = None
	if "region" in pokemon_data:
		region_id = get_fk_id("regions", pokemon_data["region"], conn_arg=conn)

	variant = None
	if "variant" in pokemon_data:
		variant = pokemon_data["variant"]

	pokemon_id = get_pokemon_id(pokemon_data["pokemon"], region_id, variant)

	# now, we check whether this competitive_pokemon exists
	existing_competitive_pokemon_query_string = """
	select
	id
	from competitive_pokemon
	where
	pokemon_id = '{}'
	  and ability_id = '{}'
	  and tera_type_id = '{}'
	""".format(pokemon_id, 
			   ability_id,  
			   tera_type_id 
			   )

	if held_item_id is not None:
		existing_competitive_pokemon_query_string += " and held_item_id = '{}'".format(held_item_id)

	for i in range(0, len(move_ids)):
		existing_competitive_pokemon_query_string += " and move_{}_id = '{}'".format((str(i + 1)), str(move_ids[i]))

	if closed_team_sheet:
		nature_id = get_fk_id("natures", pokemon_data["nature"], conn_arg=conn)
		existing_competitive_pokemon_query_string += " and nature_id = '{}'".format(nature_id)

		for iv in ivs_l:
			existing_competitive_pokemon_query_string += " and {} = '{}'".format(iv, pokemon_data["ivs"][iv])

		for ev in evs_l:
			existing_competitive_pokemon_query_string += " and {} = '{}'".format(ev, pokemon_data["evs"][ev])

	existing_result_df = pd.read_sql(existing_competitive_pokemon_query_string, conn)

	if len(existing_result_df.index) > 1:
		warnings.warn("This Pokemon is duplicated in competitive_pokemon")
		pp.pprint(pokemon_data)
		return existing_result_df.at[0, "id"]
	elif len(existing_result_df.index) == 1:
		return existing_result_df.at[0, "id"]

	# if this chunk of code is running, then a competitive pokemon with these exact attributes was not found in the database
	# therefore, we need to insert a row

	if closed_team_sheet:
		insert = {
		  "pokemon_id": pokemon_id,
		  "ability_id": ability_id,
		  "tera_type_id": tera_type_id,
		  "attack_iv": pokemon_data["ivs"]["attack_iv"],
		  "special_attack_iv": pokemon_data["ivs"]["special_attack_iv"],
		  "speed_iv": pokemon_data["ivs"]["speed_iv"],
		  "nature_id": nature_id,
		  "hp_evs": pokemon_data["evs"]["hp_evs"],
		  "attack_evs": pokemon_data["evs"]["attack_evs"],
		  "defense_evs": pokemon_data["evs"]["defense_evs"],
		  "special_attack_evs": pokemon_data["evs"]["special_attack_evs"],
		  "special_defense_evs": pokemon_data["evs"]["special_defense_evs"],
		  "speed_evs": pokemon_data["evs"]["speed_evs"]
		}
	else:
		insert = {
		  "pokemon_id": pokemon_id,
		  "ability_id": ability_id,
		  "tera_type_id": tera_type_id
		}

	if held_item_id is not None:
		insert["held_item_id"] = held_item_id
	
	# recall that move_ids was sorted above
	for i in range(0, len(move_ids)):
		insert["move_{}_id".format(str(i+1))] = move_ids[i]

	insert_row(insert, "competitive_pokemon", conn)

	# now, we can run the same query from above which failed to find this unique pokemon
	# it should return the id of our inserted row
	existing_result_df = pd.read_sql(existing_competitive_pokemon_query_string, conn)
	if len(existing_result_df.index) > 1:
		raise Exception("New competitive_pokemon row was inserted multiple times.")
	elif len(existing_result_df.index) == 1:
		return existing_result_df.at[0, "id"]
	else:
		raise Exception("New competitive_pokemon row was not inserted properly.")

