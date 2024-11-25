import json
import numpy as np
import pandas as pd
import pytest

from helpers.establish_db_connection import get_db_engine

engine = get_db_engine()
conn = engine.connect()

class TestMoves:
	def test_valid_special_categories(self):
		valid_special_categories = ["Punching", 
									"OHKO", 
									"Dance", 
									"Slicing", 
									"Wind", 
									"Binding", 
									"Biting", 
									"Sound", 
									"Powder",
									"Explosive",
									"Ball and Bomb",
									"Aura and Pulse"]

		def valid_func(l):
			if l == None:
				return True
			elif type(l) != list:
				return False

			for category in l:
				if category not in valid_special_categories:
					return False

			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df['special_categories'].apply(lambda x: valid_func(x))

		assert len(df.loc[df['valid'] == False].index) == 0

	def test_valid_additional_effects(self):
		valid_additional_effects = ["status_effect", 
									"stat_change",
									"charge", 
									"flinch", 
									"punish_minimize", 
									"multihit",
									"recoil",
									"fixed_damage",
									"punish_invulnerable",
									"weather_accuracy",
									"recharge",
									"special_damage",
									"heal_damage_percentage",
									"increased_critical_ratio",
									"binding",
									"hits_invulnerable",
									"heal_max_hp_percentage",
									"disjointed",
									"set_field_effect",
									"only_first_turn",
									"negatively_scale_user_hp",
									"thaw_user",
									"thaw_target",
									"guaranteed_critical",
									"protect",
									"unique_move",
									"redirects",
									"switch_out",
									"sucker"]

		def check_valid_additional_effects(d):
			if d is None:
				return True

			if not type(d) == dict:
				return False

			for key in d.keys():
				if key not in valid_additional_effects:
					return False

			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid_additional_effects'] = df["additional_effects"].apply(lambda x: check_valid_additional_effects(x))

		assert(len(df.loc[df["valid_additional_effects"] == False].index)) == 0

	def test_status_effect_keys(self):
		def valid_effect_keys(d):
			if type(d) == dict and "status_effect" in d:
				if not list(sorted(d["status_effect"].keys())) == ["probability", "status"]:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid_status_effect_keys'] = df["additional_effects"].apply(lambda x: valid_effect_keys(x))

		assert len(df.loc[df["valid_status_effect_keys"] == False].index) == 0

	def test_valid_status(self):
		valid_statuses = ["Burn", "Paralysis", "Freeze", "Poison", "Sleep", "Confusion", "Toxic"]

		def valid_status(d):
			if type(d) == dict and "status_effect" in d:
				if d["status_effect"]["status"] not in valid_statuses:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid_status'] = df["additional_effects"].apply(lambda x: valid_status(x))

		assert len(df.loc[df["valid_status"] == False].index) == 0

	def test_valid_status_probability(self):
		def valid_status_probability(d):
			if type(d) == dict and "status_effect" in d:
				if d["status_effect"]["probability"] <= 0 or d["status_effect"]["probability"] > 1:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid_status_probability'] = df["additional_effects"].apply(lambda x: valid_status_probability(x))

		assert len(df.loc[df["valid_status_probability"] == False].index) == 0

	def test_stat_change_keys(self):
		def valid_func(d):
			if type(d) == dict and "stat_change" in d:
				if not type(d["stat_change"]) == list:
					return False

				for sc in d["stat_change"]:
					if not list(sorted(sc.keys())) == ["effects", "probability", "stages", "stat"]:
						return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_stat_change_effects(self):
		valid_values = ["target", "self"]

		def valid_func(d):
			if type(d) == dict and "stat_change" in d:
				for sc in d["stat_change"]:
					if sc["effects"] not in valid_values:
						return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_stat_change_stat(self):
		valid_values = ["Attack", "Defense", "Special Attack", "Special Defense", "Speed", "Accuracy", "Evasion", "Critical Hit Ratio", "Omniboost"]

		def valid_func(d):
			if type(d) == dict and "stat_change" in d:
				for sc in d["stat_change"]:
					if sc["stat"] not in valid_values:
						return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_stat_change_stages(self):
		def valid_func(d):
			if type(d) == dict and "stat_change" in d:
				for sc in d["stat_change"]:
					if not type(sc["stages"]) == int or sc["stages"] < -2 or sc["stages"] > 3:
						return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_stat_change_probability(self):
		def valid_func(d):
			if type(d) == dict and "stat_change" in d:
				for sc in d["stat_change"]:
					if not type(sc["probability"]) in [float, int] or sc["probability"] <= 0 or sc["probability"] > 1:
						return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0


	def test_bypass_immunity_value(self):
		valid_values = ["Flying"]

		def valid_func(d):
			if type(d) == dict and "immunity_bypass" in d:
				if d["immunity_bypass"] not in valid_values:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0


	def test_null_hits(self):
		def valid_move(s):
			if s["category"] in ["Physical", "Special"] and np.isnan(s["hits"]):
				if s["special_categories"] and "OHKO" in s["special_categories"]:
					return True
				elif s["additional_effects"] and "multihit" in s["additional_effects"]:
					return True
				elif s["additional_effects"] and "disjointed" in s["additional_effects"]:
					return True
				elif s["unimplemented"] == True:
					return True
				else:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df.apply(lambda x: valid_move(x), axis=1)

		assert len(df.loc[df['valid'] == False].index) == 0

	def test_null_power(self):
		def valid_func(s):
			if s["category"] in ["Physical", "Special"] and np.isnan(s["power"]):
				if s["special_categories"] and "OHKO" in s["special_categories"]:
					return True
				elif s["additional_effects"] and "fixed_damage" in s["additional_effects"]:
					return True
				elif s["additional_effects"] and "special_damage" in s["additional_effects"]:
					return True
				elif s["additional_effects"] and "disjointed" in s["additional_effects"]:
					return True
				elif s["unimplemented"] == True:
					return True
				else:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df.apply(lambda x: valid_func(x), axis=1)

		assert len(df.loc[df['valid'] == False].index) == 0

	def test_charge_value(self):
		valid_values = ["Flying"]

		def valid_func(d):
			if type(d) == dict and "charge" in d:
				if d["charge"] not in valid_values:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_flinch_value(self):
		def valid_func(d):
			if type(d) == dict and "flinch" in d:
				if d["flinch"] <= 0 or d["flinch"] > 1:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid_status_probability'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid_status_probability"] == False].index) == 0

	def test_multihit_value(self):
		valid_values = ["variable"]

		def valid_func(d):
			if type(d) == dict and "multihit" in d:
				if d["multihit"] not in valid_values:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_recoil_keys(self):
		def valid_func(d):
			if type(d) == dict and "recoil" in d:
				if not list(sorted(d["recoil"].keys())) == ["percentage", "type"]:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_recoil_percentage_value(self):
		def valid_func(d):
			if type(d) == dict and "recoil" in d:
				if not type(d["recoil"]["percentage"]) == list or not len(d["recoil"]["percentage"]) == 2 or not type(d["recoil"]["percentage"][0]) == int or not type(d["recoil"]["percentage"][1]) == int:
					return False
				recoil_percentage = d["recoil"]["percentage"][0] / d["recoil"]["percentage"][1]
				if recoil_percentage <= 0 or recoil_percentage > 1:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_recoil_type_value(self):
		valid_values = ["percent_damage"]

		def valid_func(d):
			if type(d) == dict and "recoil" in d:
				if d["recoil"]["type"] not in valid_values:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_fixed_damage_value(self):
		def valid_func(d):
			if type(d) == dict and "fixed_damage" in d:
				if not type(d["fixed_damage"]) == int or d["fixed_damage"] <= 0 or d["fixed_damage"] > 50:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_special_damage_value(self):
		valid_values = ["target_weight", 
						"halve_hp", 
						"self_hp_low", 
						"pain_split", 
						"endeavor", 
						"relative_speed_low", 
						"relative_speed", 
						"relative_weight",
						"target_hp"]

		def valid_func(d):
			if type(d) == dict and "special_damage" in d:
				if d["special_damage"] not in valid_values:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_heal_damage_percentage_value(self):
		def valid_func(d):
			if type(d) == dict and "heal_damage_percentage" in d:
				if not type(d["heal_damage_percentage"]) == float or d["heal_damage_percentage"] <= 0 or d["heal_damage_percentage"] > 0.75:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_weather_accuracy_value(self):
		valid_values = ["snow", "rain"]

		def valid_func(d):
			if type(d) == dict and "weather_accuracy" in d:
				if d["weather_accuracy"] not in valid_values:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_punish_invulnerable_value(self):
		valid_values = ["air", "underwater", "underground"]

		def valid_func(d):
			if type(d) == dict and "punish_invulnerable" in d:
				if d["punish_invulnerable"] not in valid_values:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_hits_invulnerable_value(self):
		valid_values = ["air"]

		def valid_func(d):
			if type(d) == dict and "hits_invulnerable" in d:
				if d["hits_invulnerable"] not in valid_values:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_heal_max_hp_percentage_value(self):
		def valid_func(d):
			if type(d) == dict and "heal_max_hp_percentage" in d:
				if not type(d["heal_max_hp_percentage"]) == float or d["heal_max_hp_percentage"] <= 0 or d["heal_max_hp_percentage"] > 0.5:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_disjointed_value(self):
		def valid_func(d):
			if type(d) == dict and "disjointed" in d:
				if not type(d["disjointed"]) == list:
					return False
				else:
					for val in d["disjointed"]:
						if not type(val) == int or val <= 0 or val > 60:
							return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_set_field_effect_keys(self):
		def valid_func(d):
			if type(d) == dict and "set_field_effect" in d:
				if not list(sorted(d["set_field_effect"].keys())) == ["name", "type"]:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_field_effect_dict(self):
		def valid_func(d):
			if type(d) == dict and "set_field_effect" in d:
				if d["set_field_effect"]["type"] == "weather" and d["set_field_effect"]["name"] in ["Sandstorm", "Rain", "Sun", "Snow"]:
					return True
				elif d["set_field_effect"]["type"] == "speed_control" and d["set_field_effect"]["name"] in ["Tailwind", "Trick Room"]:
					return True
				elif d["set_field_effect"]["type"] == "terrain" and d["set_field_effect"]["name"] in ["Grassy Terrain", "Misty Terrain", "Electric Terrain", "Psychic Terrain"]:
					return True
				else:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_protect_type_value(self):
		valid_values = ["all", "damaging"]

		def valid_func(d):
			if type(d) == dict and "protect" in d:
				if d["protect"] not in valid_values:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_valid_unique_move_value(self):
		valid_values = ["Pollen Puff", "Ivy Cudgel", "Spiky Shield", "Burning Bulwark"]

		def valid_func(d):
			if type(d) == dict and "unique_move" in d:
				if d["unique_move"] not in valid_values:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0
		


		
