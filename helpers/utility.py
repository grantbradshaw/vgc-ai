from sqlalchemy import text

from helpers.establish_db_connection import get_db_engine

# helper function to get id for simple reference tables
# by default, this function expects that finding a result is desired
# if allow_none is set to True, a return value of None is permitted
def get_fk_id(table, name, conn_arg=None, allow_none=False):
	if table not in ["regions", "types", "natures", "abilities", "egg_groups", "held_items", "moves", "regulations"]:
		raise Exception("Table {} does not cohere to an id / name schema.".format(table))

	if conn_arg == None:
		engine = get_db_engine()
		conn = engine.connect()
	else:
		conn = conn_arg

	fk_id = None
	result = conn.execute(text("SELECT id from {} where name = '{}'".format(table, name)))
	for row in result:
		if fk_id is not None:
			raise Exception("Unexpected duplicate row in table {} for name {}".format(table, name))
		else:
			fk_id = row[0]

	if fk_id is None and not allow_none:
		raise Exception("Could not find row in table {} with name {}.".format(table, name))

	if conn_arg == None:
		conn.close()

	return fk_id


def get_pokemon_id(name, region_id, variant):
	engine = get_db_engine()
	with engine.connect() as conn:
		# if no region_id is passed, then this is either a pokemon with no regional variants or the first instance of it
		if variant is None and region_id is None:
			query_string = "SELECT id from pokemon where name = '{}' order by region_id asc limit 1".format(name)
		elif variant is None and region_id is not None:
			query_string = "SELECT id from pokemon where name = '{}' and region_id = '{}'".format(name, region_id)
		elif variant is not None and region_id is None:
			query_string = "SELECT id from pokemon where name = '{}' and variant = '{}' order by region_id asc limit 1".format(name, variant)
		elif variant is not None and region_id is not None:
			query_string = "SELECT id from pokemon where name = '{}' and variant = '{}' and region_id = '{}'".format(name, variant, region_id)

		result = conn.execute(text(query_string))
		pokemon_id = None

		for row in result:
			if pokemon_id is None:
				pokemon_id = row[0]
			else:
				raise Exception("Unexpected ambiguous result for name = {}, region_id = {}, variant = {}".format(name, region_id, variant))

		if pokemon_id is None:
			raise Exception("Could not find pokemon with name = {}, region_id = {}, variant = {}".format(name, region_id, variant))

		return pokemon_id

