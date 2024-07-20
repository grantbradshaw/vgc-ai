import json
import math
import pandas as pd

from helpers.establish_db_connection import get_db_engine

class Team:
	def __init__(self, team_id):
		engine = get_db_engine()
		with engine.connect() as conn:
			team_df = pd.read_sql("SELECT * from teams where id = '{}'".format(team_id), conn)

			if len(team_df.index) == 0:
				raise Exception("No team with id {} in database.".format(team_id))

			party = []

			for i in range (1,7):
				party.append(Pokemon(team_df['competitive_pokemon_{}_id'.format(i)].iloc[0]))

			self.party = party

class Pokemon:
	def __init__(self, competitive_pokemon_id):
		engine = get_db_engine()
		with engine.connect() as conn:
			comp_pokemon_df = pd.read_sql("SELECT * from competitive_pokemon where id = '{}'".format(competitive_pokemon_id), conn)

			if len(comp_pokemon_df.index) == 0:
				raise Exception("No competitive pokemon with id {} in database.".format(competitive_pokemon_id))

			pokemon_df = pd.read_sql("SELECT * from pokemon where id = '{}'".format(comp_pokemon_df['pokemon_id'].iloc[0]), conn)

			if len(pokemon_df.index) == 0:
				raise Exception("No pokemon with id {} in database.".format(comp_pokemon_df['pokemon_id'].iloc[0]))

			nature_df = pd.read_sql("SELECT * from natures where id = '{}'".format(comp_pokemon_df['nature_id'].iloc[0]), conn)
			if len(nature_df.index) == 0:
				raise Exception("No nature with id {} in database.".format(comp_pokemon_df['nature_id'].iloc[0]))

			# see https://bulbapedia.bulbagarden.net/wiki/Stat for formulas
			# IVs are assumed to be 31 unless stated otherwise
			self.hp = math.floor(((2 * pokemon_df['hp'].iloc[0]) + 31 + math.floor(comp_pokemon_df['hp_evs'].iloc[0] * 0.25)) * 50 * 0.01) + 50 + 10

			other_stats = {
				"Attack": math.floor((math.floor(0.01 * (2 * pokemon_df['attack'].iloc[0] + comp_pokemon_df['attack_iv'].iloc[0] + math.floor(0.25 * comp_pokemon_df['attack_evs'].iloc[0])) * 50) + 5)),
				"Defense": math.floor((math.floor(0.01 * (2 * pokemon_df['defense'].iloc[0] + 31 + math.floor(0.25 * comp_pokemon_df['defense_evs'].iloc[0])) * 50) + 5)),
				"Special Attack": math.floor((math.floor(0.01 * (2 * pokemon_df['special_attack'].iloc[0] + comp_pokemon_df['special_attack_iv'].iloc[0] + math.floor(0.25 * comp_pokemon_df['special_attack_evs'].iloc[0])) * 50) + 5)),
				"Special Defense": math.floor((math.floor(0.01 * (2 * pokemon_df['special_defense'].iloc[0] + 31 + math.floor(0.25 * comp_pokemon_df['special_defense_evs'].iloc[0])) * 50) + 5)),
				"Speed": math.floor((math.floor(0.01 * (2 * pokemon_df['speed'].iloc[0] + comp_pokemon_df['speed_iv'].iloc[0] + math.floor(0.25 * comp_pokemon_df['speed_evs'].iloc[0])) * 50) + 5))
			}

			if nature_df["boosting_stat"].iloc[0] != nature_df["decreasing_stat"].iloc[0]:
				other_stats[nature_df["boosting_stat"].iloc[0]] = math.floor(other_stats[nature_df["boosting_stat"].iloc[0]] * 1.1)
				other_stats[nature_df["decreasing_stat"].iloc[0]] = math.floor(other_stats[nature_df["decreasing_stat"].iloc[0]] * 0.9)

			self.attack = other_stats["Attack"]
			self.defense = other_stats["Defense"]
			self.special_attack = other_stats["Special Attack"]
			self.special_defense = other_stats["Special Defense"]
			self.speed = other_stats["Speed"]

			self.weight_kg = pokemon_df['weight_kg'].iloc[0]

			ability_df = pd.read_sql("SELECT * FROM natures where id = '{}'".format(comp_pokemon_df['nature_id'].iloc[0]), conn)

			self.ability = ability_df['name'].iloc[0]

			tera_type_df = pd.read_sql("SELECT * FROM types where id = '{}'".format(comp_pokemon_df['tera_type_id'].iloc[0]), conn)

			self.tera_type = tera_type_df['name'].iloc[0]

			self.moves = []

			for i in range(1,5):
				move_df = pd.read_sql("SELECT * FROM detailed_moves where id = ")





