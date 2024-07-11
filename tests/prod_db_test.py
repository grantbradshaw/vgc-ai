import json
import pandas as pd

from helpers.establish_db_connection import get_db_engine

engine = get_db_engine()
conn = engine.connect()

class TestMoves:
	def test_invalid_special_categories(self):
		valid_special_categories = ["Punching"]

		def valid_category(l):
			l = list(filter(lambda x: len(x) > 0, l))
			for category in l:
				if category not in valid_special_categories:
					return False
			return True

		df = pd.read_sql("SELECT * from detailed_moves", conn)
		df['valid_special_category'] = df["special_categories"].apply(lambda x: valid_category(x))

		assert len(df.loc[df["valid_special_category"] == False].index) == 0




		

		


		
