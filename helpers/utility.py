import pandas as pd
from sqlalchemy import text

from helpers.establish_db_connection import get_db_engine

# helper function to get id for simple reference tables
# by default, this function expects that finding a result is desired
# if allow_none is set to True, a return value of None is permitted
def get_fk_id(table, name, conn_arg=None, allow_none=False):
	if table not in ["regions", "types", "natures", "abilities", "egg_groups", "held_items", "moves", "regulations"]:
		raise Exception("Table {} does not cohere to an id / name schema.".format(table))

	# allow_none is intended to allow failing to find a name
	# however, if get_fk_id is passed a "null" value, this function simply bounces it back
	# by extension, this function will not search null names
	if name == "" or name == None or pd.isnull(name):
		return None

	if conn_arg == None:
		engine = get_db_engine()
		conn = engine.connect()
	else:
		conn = conn_arg

	fk_id = None
	result = conn.execute(text("SELECT id from {} where name = '{}'".format(table, name.replace("'", "''"))))
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

# expects a dictionary of format {"column": "value",...}
# this must be passed a connection - this helper is intended to be run as part of a transaction and does not commit
def insert_row(insert, table, conn):
	if not isinstance(insert, dict):
		raise Exception("insert_row expects a dictionary, but received arg of type {}".format(str(type(insert))))

	columns = []
	values = []

	for key, value in insert.items():
		if value == "":
			continue
		columns.append(key)
		values.append(str(value))

	conn.execute(text("INSERT INTO {} ({}) VALUES ({})".format(table, ",".join(columns), "'" + "','".join(values) + "'")))

	return True


def get_pokemon_id(name, region_id, variant, conn_arg=None):
	if conn_arg == None:
		engine = get_db_engine()
		conn = engine.connect()
	else:
		conn = conn_arg

	
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

	if conn_arg == None:
		conn.close()

	return pokemon_id

