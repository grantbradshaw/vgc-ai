from helpers.battle.battle_classes import Battle, Team, Pokemon
from helpers.establish_db_connection import get_db_engine
from helpers.utility import generate_unique_team_sequences

import copy
import pandas as pd
import pprint

pp = pprint.PrettyPrinter(indent=2)

team_1_id = 319 # https://pokepast.es/3944b7ef263e6779
team_2_id = 320 # https://pokepast.es/76f9ee3f804535d0

team_seq_permutations = generate_unique_team_sequences()

pokemon = {"team_1": [],
		   "team_2": []}

engine = get_db_engine()
with engine.connect() as conn:
	team_1_df = pd.read_sql("SELECT * from teams where id = '{}'".format(team_1_id), conn)
	team_2_df = pd.read_sql("SELECT * from teams where id = '{}'".format(team_2_id), conn)

	if len(team_1_df.index) == 0:
		raise Exception("No team with id {} in database.".format(team_1_id))
	if len(team_2_df.index) == 0:
		raise Exception("No team with id {} in database.".format(team_2_id))

	for i in range(1,7):
		pokemon["team_1"].append(copy.deepcopy(Pokemon(team_1_df['competitive_pokemon_{}_id'.format(i)].iloc[0])))
		pokemon["team_2"].append(copy.deepcopy(Pokemon(team_2_df['competitive_pokemon_{}_id'.format(i)].iloc[0])))

for team_1_sequence in team_seq_permutations:
	for team_2_sequence in team_seq_permutations:
		team_1 = []
		for i in team_1_sequence:
			team_1.append(pokemon["team_1"][i - 1])

		team_2 = []
		for j in team_2_sequence:
			team_2.append(pokemon["team_2"][j-1])

		battle = Battle(Team(team_1), Team(team_2))
		battle.begin()
