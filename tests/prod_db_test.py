import json
import pandas as pd

from helpers.establish_db_connection import get_db_engine

engine = get_db_engine()
conn = engine.connect()

class TestMoves:
	def test_invalid_special_categories(self):
		valid_special_categories = ["Punching", "OHKO"]

		def valid_category(l):
			l = list(filter(lambda x: len(x) > 0, l))
			for category in l:
				if category not in valid_special_categories:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid_special_category'] = df["special_categories"].apply(lambda x: valid_category(x))

		assert len(df.loc[df["valid_special_category"] == False].index) == 0

	def test_status_effect_keys(self):
		def valid_effect_keys(d):
			if type(d) == dict and "status_effect" in d:
				if not "status" in d["status_effect"] or not "probability" in d["status_effect"]:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid_status_effect_keys'] = df["additional_effects"].apply(lambda x: valid_effect_keys(x))

		assert len(df.loc[df["valid_status_effect_keys"] == False].index) == 0

	def test_valid_status(self):
		valid_statuses = ["Burn", "Paralysis", "Freeze"]

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





		

		


		
