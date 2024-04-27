import json
from sqlalchemy import text
from helpers.establish_db_connection import get_db_engine

# load_data is always destructive, as the data being loaded here should never be updated directly in the database. 
def initialize_data():
	engine = get_db_engine()
	with engine.connect() as conn:
		with open("data/regions.json") as region_infile:
			regions = json.load(region_infile)
		conn.execute(text("DELETE FROM regions"))
		conn.execute(text("ALTER SEQUENCE regions_id_seq RESTART WITH 1"))
		for region in regions:
			conn.execute(text("INSERT INTO regions (name) VALUES ('{}')".format(region)))

		with open("data/types.json") as type_infile:
			types = json.load(type_infile)
		conn.execute(text("DELETE FROM types"))
		conn.execute(text("ALTER SEQUENCE types_id_seq RESTART WITH 1"))
		for poke_type in types:
			conn.execute(text("INSERT INTO types (name) VALUES ('{}')".format(poke_type)))

		with open("data/natures.json") as nature_infile:
			natures = json.load(nature_infile)
		conn.execute(text("DELETE FROM natures"))
		conn.execute(text("ALTER SEQUENCE natures_id_seq RESTART WITH 1"))
		for nature in natures:
			conn.execute(text("INSERT INTO natures (name) VALUES ('{}')".format(nature)))

		with open("data/abilities.json") as ability_infile:
			abilities = json.load(ability_infile)
		conn.execute(text("DELETE FROM abilities"))
		conn.execute(text("ALTER SEQUENCE abilities_id_seq RESTART WITH 1"))
		# As the plain text json contains single quotations, they must be reformatted appropriately for Postgres
		for ability in abilities:
			conn.execute(text("INSERT INTO abilities (name) VALUES ('{}')".format(ability.replace("'", "''"))))

		with open("data/egg_groups.json") as egg_group_infile:
			egg_groups = json.load(egg_group_infile)
		conn.execute(text("DELETE FROM egg_groups"))
		conn.execute(text("ALTER SEQUENCE egg_groups_id_seq RESTART WITH 1"))
		for egg_group in egg_groups:
			conn.execute(text("INSERT INTO egg_groups (name) VALUES ('{}')".format(egg_group)))

		with open("data/held_items.json") as held_items_infile:
			held_items = json.load(held_items_infile)
		conn.execute(text("DELETE FROM held_items"))
		conn.execute(text("ALTER SEQUENCE held_items_id_seq RESTART WITH 1"))
		for held_item in held_items:
			conn.execute(text("INSERT INTO held_items (name) VALUES ('{}')".format(held_item.replace("'", "''"))))
		
		conn.commit()

initialize_data()




