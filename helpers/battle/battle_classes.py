import copy
import json
import math
import pandas as pd

from helpers.establish_db_connection import get_db_engine

class Battle:
	def __init__(self, team_1, team_2):
		self.team_1 = team_1
		self.team_2 = team_2

	def begin(self):
		self._simulate_turn()

	def _simulate_turn(self):
		team_1_candidates = self.team_1.generate_candidate_lines(self.team_2.get_pokemon_count("Field"))
		team_2_candidates = self.team_2.generate_candidate_lines(self.team_1.get_pokemon_count("Field"))

		for team_1_line in team_1_candidates:
			for team_2_line in team_2_candidates:
				self._resolve_turn(team_1_line, team_2_line)
				raise Exception("force stop")


	def _resolve_turn(self, team_1_line, team_2_line):
		team_1 = copy.deepcopy(self.team_1)
		team_2 = copy.deepcopy(self.team_2)

class Team:
	def __init__(self, pokemon_list):
			if not type(pokemon_list) == list:
				raise Exception("team_selection must be a list")

			if len(set(pokemon_list)) != 4:
				raise Exception("team_selection must contain 4 unique values")

			self.field = pokemon_list[0:2]
			self.party = pokemon_list[2:4]

			self.terastallized = False

	def get_pokemon_count(self, field_or_party):
		if field_or_party == "Field":
			return len(list(filter(lambda x: x.hp > 0, self.field)))
		elif field_or_party == "Party": 
			return len(list(filter(lambda x: x.hp > 0, self.party)))
		else:
			raise Exception("field_or_party only accepts 'Field' or 'Party' but received {}".format(field_or_party))

	def generate_candidate_lines(self, alive_opposing_field_pokemon):
		alive_field_pokemon = self.get_pokemon_count("Field")
		alive_party_pokemon = self.get_pokemon_count("Party")

		left_lines = []

		if alive_party_pokemon > 0:
			for alive_pokemon in self.party:
				left_lines.append({"type": "switch", "target": alive_pokemon})

		for move_name in self.field[0].moves:
			left_lines.extend(self._produce_move_lines(self.field[0].moves[move_name], alive_opposing_field_pokemon, alive_field_pokemon))

		if alive_field_pokemon == 2:
			right_lines = []
			if alive_party_pokemon > 0:
				for alive_pokemon in self.party:
					right_lines.append({"type": "switch", "target": alive_pokemon})
			for move_name in self.field[1].moves:
				right_lines.extend(self._produce_move_lines(self.field[1].moves[move_name], alive_opposing_field_pokemon, alive_field_pokemon))

		lines = []

		if alive_field_pokemon == 1:
			for left_line in left_lines:
				lines.append({self.field[0]: left_line})
		else:
			for left_line in left_lines:
				for right_line in right_lines:
					# both slots cannot switch to the same Pokemon
					if left_line["type"] == "switch" and right_line["type"] == "switch" and left_line["target"] == right_line["target"]:
						continue
					else:
						lines.append({self.field[0]: left_line, self.field[1]: right_line})

		return lines

	def _produce_move_lines(self, move, alive_opposing_field_pokemon, alive_field_pokemon):
		lines = []

		if move["targets"] in ["Single", "Opponent"]:
			lines.append({"type": "move", "target": "opponent_left", "move": move})
			# technically you can target empty slots, but it gets redirected anyway
			if alive_opposing_field_pokemon == 2:
				lines.append({"type": "move", "target": "opponent_right", "move": move})

		if move["targets"] in ["Self", "Self or Ally"]:
			lines.append({"type": "move", "target": "self", "move": move})
		
		# I am unsure if you are allowed to target an empty ally slot
		if move["targets"] in ["Self or Ally", "Ally", "Single"] and alive_field_pokemon == 2:
			lines.append({"type": "move", "target": "ally", "move": move})

		if move["targets"] in ["Ally and Opponents", "All", "Party", "Team", "Field - Team", "Field - Opponents", "Field"]:
			snake_target = move["targets"].replace("-", "").split(" ")
			snake_target = list(filter(lambda x: len(x) > 0, snake_target))
			snake_target = list(map(lambda x: x.lower(), snake_target))
			snake_target = "_".join(snake_target)
			lines.append({"type": "move", "target": snake_target, "move": move})

		return lines

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
			self.max_hp = self.hp

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

			ability_df = pd.read_sql("SELECT * FROM abilities where id = '{}'".format(comp_pokemon_df['ability_id'].iloc[0]), conn)

			self.ability = ability_df['name'].iloc[0]

			types = []

			type_1_df = pd.read_sql("SELECT * FROM types where id = '{}'".format(pokemon_df["type_1_id"].iloc[0]), conn)
			types.append(type_1_df['name'].iloc[0])
			if not pd.isnull(pokemon_df["type_2_id"].iloc[0]):
				type_2_df = pd.read_sql("SELECT * FROM types where id = '{}'".format(pokemon_df["type_2_id"].iloc[0]), conn)
				types.append(type_2_df['name'].iloc[0])

			self.types = types

			tera_type_df = pd.read_sql("SELECT * FROM types where id = '{}'".format(comp_pokemon_df['tera_type_id'].iloc[0]), conn)

			self.tera_type = tera_type_df['name'].iloc[0]

			moves = {}

			for i in range(1,5):
				move_df = pd.read_sql("SELECT * FROM detailed_moves where id = '{}'".format(comp_pokemon_df['move_{}_id'.format(str(i))].iloc[0]), conn)
				if move_df['unimplemented'].iloc[0] == True:
					raise Exception("Cannot load Pokemon with unimplemented move - {}".format(move_df['name'].iloc[0]))

				move_type_df = pd.read_sql("SELECT * FROM types where id = '{}'".format(move_df['type'].iloc[0]), conn)

				moves[move_df['name'].iloc[0]] = {"type": move_type_df['name'].iloc[0],
												  "category": move_df['category'].iloc[0],
												  "targets": move_df['targets'].iloc[0],
												  "hits": move_df['hits'].iloc[0],
												  "power": move_df['power'].iloc[0],
												  "accuracy": move_df['accuracy'].iloc[0],
												  "priority": move_df['priority'].iloc[0],
												  "contact": move_df['contact'].iloc[0],
												  "special_categories": move_df['special_categories'].iloc[0],
												  "additional_effects": move_df['additional_effects'].iloc[0]}
			
			self.moves = moves
			self.terastallized = False
