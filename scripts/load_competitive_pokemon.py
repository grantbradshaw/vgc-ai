import csv
import numpy as np
import pandas as pd
import pprint
import re
from sqlalchemy import text
import sys
import warnings

from helpers.establish_db_connection import get_db_engine
from helpers.utility import get_fk_id, get_pokemon_id
from helpers.read_pokepaste import extract_paste

pp = pprint.PrettyPrinter(indent=2)

# by default, this function will not wipe the relevant tables
# this allows appending to "data/ladder_dump.csv" to add to the tables
# however, the function can wipe the tables if it is passed command line argument --force-reload
# note that even if loading the file does not complete, the tables will still be wiped (because of the caching pattern)
def load_competitive_pokemon():
	if "--force-reload" in sys.argv:
		force_reload = True
	else:
		force_reload = False

	engine = get_db_engine()
	with engine.connect() as conn:
		if force_reload:
			conn.execute(text("DELETE FROM team_references"))
			conn.execute(text("ALTER SEQUENCE team_references_id_seq RESTART WITH 1"))
			conn.execute(text("DELETE FROM teams"))
			conn.execute(text("ALTER SEQUENCE teams_id_seq RESTART WITH 1"))
			conn.execute(text("DELETE FROM competitive_pokemon"))
			conn.execute(text("ALTER SEQUENCE competitive_pokemon_id_seq RESTART WITH 1"))

			conn.commit()

		with open("data/ladder_dump.csv") as ladder_infile:
			ladder_reader = csv.reader(ladder_infile)
			row_count = 0

			for row in ladder_reader:
				if row_count == 0:
					row_count += 1
				else:
					# check for valid data inputs
					regulation = row[0]
					if regulation == "":
						raise Exception("Regulation cannot be blank, was for row index {}".format(str(row_count)))

					paste_url = row[1]

					if paste_url == "":
						raise Exception("URL cannot be blank, was for row index {}".format(str(row_count)))
					if not re.match(r'^https:\/\/pokepast\.es\/[0-9a-z]{16}$', paste_url):
						raise Exception("URL {} is not a valid PokePaste url.".format(paste_url))

					# now, we check if we have already scraped this exact URL
					paste_result_df = pd.read_sql("SELECT id from teams where paste_url = '{}'".format(paste_url), conn)

					if len(paste_result_df.index) > 1:
						warnings.warn("Table teams has duplicate paste_url {}".format(paste_url))
						continue
					elif len(paste_result_df.index) == 1:
						# there is no reason to scrape a paste we have already scraped
						continue

					regulation_id = get_fk_id("regulations", regulation, conn_arg=conn)

					team = extract_paste(paste_url)

					competitive_pokemon_ids = []

					# because of validation in extract_paste, we assume that we have 6 pokemon at this point
					for pokemon_data in team:
						competitive_pokemon_ids.append(str(insert_competitive_pokemon(conn, pokemon_data)))

					# next, we check whether this exact team already exists in the database
					# this primarily catches duplicated pastes, but also covers a case where two trainers used identical teams
					team_query = """
					select
					id
					from teams
					where regulation_id = '{}'
					  and competitive_pokemon_1_id = '{}'
					  and competitive_pokemon_2_id = '{}'
					  and competitive_pokemon_3_id = '{}'
					  and competitive_pokemon_4_id = '{}'
					  and competitive_pokemon_5_id = '{}'
					  and competitive_pokemon_6_id = '{}'
					""".format(regulation_id,
							   competitive_pokemon_ids[0],
							   competitive_pokemon_ids[1],
							   competitive_pokemon_ids[2],
							   competitive_pokemon_ids[3],
							   competitive_pokemon_ids[4],
							   competitive_pokemon_ids[5]
							  )

					duplicate_team_result = conn.execute(text(team_query))

					duplicate_team = False
					team_id = None

					for duplicate_team_row in duplicate_team_result:
						if duplicate_team == False:
							duplicate_team = True
							team_id = duplicate_team_row[0]
						else:
							warnings.warn("Table teams already has a duplicated row. See the following query")
							pp.pprint(duplicate_team_query)

					if not duplicate_team:

						insert = {
							"regulation_id": regulation_id,
							"competitive_pokemon_1_id": competitive_pokemon_ids[0],
							"competitive_pokemon_2_id": competitive_pokemon_ids[1],
							"competitive_pokemon_3_id": competitive_pokemon_ids[2],
							"competitive_pokemon_4_id": competitive_pokemon_ids[3],
							"competitive_pokemon_5_id": competitive_pokemon_ids[4],
							"competitive_pokemon_6_id": competitive_pokemon_ids[5],
							"paste_url": paste_url
						}

						columns = []
						values = []

						for key, value in insert.items():
							columns.append(key)
							values.append(str(value))

						conn.execute(text("INSERT INTO teams ({}) VALUES ({})".format(",".join(columns), "'" + "','".join(values) + "'")))

						# we must then get back the id of the team inserted
						inserted_team_query = team_query + " and paste_url = '{}'".format(paste_url)
						inserted_team_result = conn.execute(text(inserted_team_query))

						for inserted_team_row in inserted_team_result:
							# which is is, because we're in this if block
							if team_id is None:
								team_id = inserted_team_row[0]
							elif team_id is not None:
								raise Exception("New teams row has been duplicated.")

						if team_id is None:
							raise Exception("An error has occurred in inserting the new team row.") 

					# finally, we insert the links to references that can help us learn more about the team
					# these include team reports, tournament games, content creator videos featuring the team, etc.
					references = list(filter(lambda x: len(x) >= 1, row[3:]))

					for reference in references:
						duplicate_reference_result = conn.execute(text("SELECT id from team_references where team_id = '{}' and reference = '{}'".format(str(team_id), reference)))
						is_duplicate_reference = False

						# we don't need to handle if is_duplicate = True, as there is a schema level uniqueness constraint
						# this validation is simply to avoid gracelessly error handling at a DB level
						for duplicate_reference_row in duplicate_reference_result:
							if is_duplicate_reference == False:
								is_duplicate_reference = True

						if not is_duplicate_reference:
							conn.execute(text("INSERT INTO team_references (team_id, reference) VALUES ({})".format("'" + str(team_id) + "','" + reference + "'")))
						

					conn.commit()

# this function inserts a row for a competitive pokemon if that unique set is not already present in the database
# then returns the id representing this unique competitive pokemon
def insert_competitive_pokemon(conn, pokemon_data):
	ability_id = get_fk_id("abilities", pokemon_data["ability"], conn_arg=conn)
	held_item_id = get_fk_id("held_items", pokemon_data["item"], conn_arg=conn)
	tera_type_id = get_fk_id("types", pokemon_data["tera_type"], conn_arg=conn)
	nature_id = get_fk_id("natures", pokemon_data["nature"], conn_arg=conn)
	# Pokepastes only lists region for variants, so None is possible
	region_id = get_fk_id("regions", pokemon_data["region"], conn_arg=conn, allow_none=True)

	pokemon_id = get_pokemon_id(pokemon_data["pokemon"], region_id, pokemon_data["variant"])

	move_ids = []
	for move in pokemon_data["moves"]:
		# by this point, empty move slots are expected to have been filtered out, so we don't allow_none
		move_id = get_fk_id("moves", move, conn_arg=conn)
		move_ids.append(move_id)

	# now, we check whether this competitive_pokemon exists
	existing_competitive_pokemon_query_string = """
	select
	id
	from competitive_pokemon
	where
	pokemon_id = '{}'
	  and ability_id = '{}'
	  and tera_type_id = '{}'
	  and attack_iv = '{}'
	  and special_attack_iv = '{}'
	  and speed_iv = '{}'
	  and nature_id = '{}'
	  and hp_evs = '{}'
	  and attack_evs = '{}'
	  and defense_evs = '{}'
	  and special_attack_evs = '{}'
	  and special_defense_evs = '{}'
	  and speed_evs = '{}'
	""".format(pokemon_id, 
			   ability_id,  
			   tera_type_id, 
			   pokemon_data["ivs"]["attack_iv"],
			   pokemon_data["ivs"]["special_attack_iv"],
			   pokemon_data["ivs"]["speed_iv"],
			   nature_id,
			   pokemon_data["evs"]["hp_evs"],
			   pokemon_data["evs"]["attack_evs"],
			   pokemon_data["evs"]["defense_evs"],
			   pokemon_data["evs"]["special_attack_evs"],
			   pokemon_data["evs"]["special_defense_evs"],
			   pokemon_data["evs"]["speed_evs"]
			   )

	if held_item_id is not None:
		existing_competitive_pokemon_query_string += " and held_item_id = '{}'".format(held_item_id)

	for i in range(0, len(move_ids)):
		existing_competitive_pokemon_query_string += " and move_{}_id = '{}'".format((str(i + 1)), str(move_ids[i]))

	existing_result = conn.execute(text(existing_competitive_pokemon_query_string))
	existing_id = None

	for row in existing_result:
		if existing_id is None:
			existing_id = row[0]
		elif existing_id is not None:
			warnings.warn("This Pokemon is duplicated in competitive_pokemon")
			pp.pprint(pokemon_data)

	if existing_id is not None:
		return existing_id

	# if this chunk of code is running, then a competitive pokemon with these exact attributes was not found in the database
	# therefore, we need to insert a row
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

	if held_item_id is not None:
		insert["held_item_id"] = held_item_id

	for i in range(0, len(list(sorted(move_ids)))):
		insert["move_{}_id".format(str(i+1))] = move_ids[i]

	columns = []
	values = []

	for key, value in insert.items():
		columns.append(key)
		values.append(str(value))

	conn.execute(text("INSERT INTO competitive_pokemon ({}) VALUES ({})".format(",".join(columns), "'" + "','".join(values) + "'")))

	# now, we can run the same query from above which failed to find this unique pokemon
	# it should return the id of our inserted row
	existing_result = conn.execute(text(existing_competitive_pokemon_query_string))
	existing_id = None

	for row in existing_result:
		if existing_id is None:
			existing_id = row[0]
		elif existing_id is not None:
			raise Exception("New competitive_pokemon row was inserted multiple times.")

	if existing_id is not None:
		return existing_id
	else:
		raise Exception("New competitive_pokemon row was not inserted properly.")


load_competitive_pokemon()
