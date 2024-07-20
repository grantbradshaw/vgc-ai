import json
import numpy as np
import pandas as pd
import pytest

from helpers.establish_db_connection import get_db_engine

engine = get_db_engine()
conn = engine.connect()

class TestMoves:
	def test_valid_special_categories(self):
		valid_special_categories = ["Punching", "OHKO", "Dance", "Slicing", "Wind", "Binding", "Biting", "Sound"]

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
									"immunity_bypass", 
									"charge", 
									"flinch", 
									"punish_minimize", 
									"multihit",
									"recoil",
									"fixed_damage"]

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
		valid_statuses = ["Burn", "Paralysis", "Freeze", "Poison", "Sleep", "Confusion"]

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
				if not list(sorted(d["stat_change"].keys())) == ["effects", "probability", "stages", "stat"]:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_stat_change_effects(self):
		valid_values = ["target"]

		def valid_func(d):
			if type(d) == dict and "stat_change" in d:
				if d["stat_change"]["effects"] not in valid_values:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_stat_change_stat(self):
		valid_values = ["Attack", "Defense", "Accuracy"]

		def valid_func(d):
			if type(d) == dict and "stat_change" in d:
				if d["stat_change"]["stat"] not in valid_values:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_stat_change_stages(self):
		def valid_func(d):
			if type(d) == dict and "stat_change" in d:
				if not type(d["stat_change"]["stages"]) == int or d["stat_change"]["stages"] < -1 or d["stat_change"]["stages"] > 2:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0

	def test_stat_change_probability(self):
		def valid_func(d):
			if type(d) == dict and "stat_change" in d:
				if not type(d["stat_change"]["probability"]) in [float, int] or d["stat_change"]["probability"] <= 0 or d["stat_change"]["probability"] > 1:
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
				if not type(d["fixed_damage"]) == int or d["fixed_damage"] <= 0 or d["fixed_damage"] > 20:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid'] = df["additional_effects"].apply(lambda x: valid_func(x))

		assert len(df.loc[df["valid"] == False].index) == 0











		

		


		
