import csv
import numpy as np
import pandas as pd
import pprint
import re
from sqlalchemy import text
import sys
import warnings

from helpers.establish_db_connection import get_db_engine
from helpers.utility import get_fk_id, get_pokemon_id, insert_row, insert_competitive_pokemon
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

					competitive_pokemon_ids.sort()

					# next, we check whether this exact team already exists in the database
					# this primarily catches duplicated pastes (i.e. different url but same data)
					# but also covers a case where two trainers used identical teams
					# we leverage the ordering of competitive_pokemon_ids in inserting the team to simplify the following query
					# otherwise we would need to explicitly rank the 6 ids to cover for the same team in a different order
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

					duplicate_team_result_df = pd.read_sql(team_query, conn)
					team_id = None

					if len(duplicate_team_result_df.index) > 1:
						warnings.warn("Table teams already has a duplicated row. See the following query")
						pp.pprint(duplicate_team_query)
						team_id = duplicate_team_result_df.at[0, "id"]
					elif len(duplicate_team_result_df.index) == 1:
						team_id = duplicate_team_result_df.at[0, "id"]

					if team_id is None:
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

						insert_row(insert, "teams", conn)
						
						# we must then get back the id of the team inserted
						inserted_team_query = team_query + " and paste_url = '{}'".format(paste_url)
						inserted_team_result_df = pd.read_sql(inserted_team_query, conn)

						if len(inserted_team_result_df.index) == 0:
							raise Exception("An error occurred inserting the new team row for paste {}".format(paste_url))
						elif len(inserted_team_result_df.index) > 1:
							raise Exception("New team row was duplicated for paste {}".format(paste_url))
						else:
							team_id = inserted_team_result_df.at[0, "id"]

					# finally, we insert the links to references that can help us learn more about the team
					# these include team reports, tournament games, content creator videos featuring the team, etc.
					references = list(filter(lambda x: len(x) >= 1, row[3:]))

					for reference in references:
						# pyscopg2 SELECT complains about single % signs in url, so we have to escape them
						duplicate_reference_result_df = pd.read_sql("SELECT id from team_references where team_id = '{}' and reference = '{}'".format(str(team_id), reference.replace("%", "%%")), conn)

						# we don't need to cover a case where the paste has been duplicated
						# as there are DB uniqueness constraints
						# this simply avoids gracelessly error handling at a DB level
						if len(duplicate_reference_result_df.index) >= 1:
							continue
						else:
							reference_insert = {"team_id": team_id,
												"reference": reference}
							insert_row(reference_insert, "team_references", conn)

					conn.commit()

load_competitive_pokemon()
