from sqlalchemy import text

from helpers.establish_db_connection import get_db_engine



# helper function to get id for simple reference tables
# by default, this function expects that finding a result is desired
# if allow_none is set to True, a return value of None is permitted
def get_fk_id(table, name, allow_none=False):
	if table not in ["regions", "types", "natures", "abilities", "egg_groups", "held_items", "moves"]:
		raise Exception("Table {} does not cohere to an id / name schema.".format(table))

	engine = get_db_engine()
	with engine.connect() as conn:
		fk_id = None
		result = conn.execute(text("SELECT id from {} where name = '{}'".format(table, name)))
		for row in result:
			if fk_id is not None:
				raise Exception("Unexpected duplicate row in table {} for name {}".format(table, name))
			else:
				fk_id = row[0]

		if fk_id is None and not allow_none:
			raise Exception("Could not find row in table {} with name {}.".format(table, name))

		return fk_id