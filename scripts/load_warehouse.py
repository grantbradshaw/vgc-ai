import json
import numpy as np
import pandas as pd
from sqlalchemy import text

from helpers.establish_db_connection import get_db_engine

def load_warehouse():
	engine = get_db_engine()
	with engine.connect() as conn:
		conn.execute(text("DELETE FROM competitive_pokemon_lookup"))

		cpl_query = """
		select
		cp.id,
		p.name as pokemon,
		r.name as region,
		p.variant as variant,
		a.name as ability,
		hi.name as held_item,
		t.name as tera_type,
		n.name as nature,
		rg.name as regulation,
		cp.attack_iv,
		cp.speed_iv,
		cp.special_attack_iv,
		cp.hp_evs,
		cp.attack_evs,
		cp.defense_evs,
		cp.special_attack_evs,
		cp.special_defense_evs,
		cp.speed_evs,
		m1.name as move_1,
		m2.name as move_2,
		m3.name as move_3,
		m4.name as move_4
		from competitive_pokemon cp
		join pokemon p 
			on cp.pokemon_id = p.id
		join regions r
			on p.region_id = r.id
		join abilities a
			on cp.ability_id = a.id
		left join held_items hi
			on cp.held_item_id = hi.id
		join types t
			on cp.tera_type_id = t.id
		join natures n
			on cp.nature_id = n.id
		-- note that if a competitive_pokemon is in multiple teams across regulations, then this table will have a row for each regulation
		-- left join ensures theory pokemon not associated with a team are included
		left join (
			select regulation_id, competitive_pokemon_1_id as cp_id FROM teams
			UNION
			select regulation_id, competitive_pokemon_2_id as cp_id  FROM teams
			UNION
			select regulation_id, competitive_pokemon_3_id as cp_id FROM teams
			UNION
			select regulation_id, competitive_pokemon_4_id as cp_id FROM teams
			UNION
			select regulation_id, competitive_pokemon_5_id as cp_id FROM teams
			UNION
			select regulation_id, competitive_pokemon_6_id as cp_id FROM teams
			GROUP BY 1,2
		) tr
			on cp.id = tr.cp_id
		join regulations rg
			on tr.regulation_id = rg.id
		join moves m1
			on cp.move_1_id = m1.id
		left join moves m2
			on cp.move_2_id = m2.id
		left join moves m3
			on cp.move_3_id = m3.id
		left join moves m4
			on cp.move_4_id = m4.id
		"""

		cpl_df = pd.read_sql(cpl_query, conn)
		cpl_df.apply(lambda x: insert_series(x, conn), axis=1)

		conn.commit()
		

def insert_series(s, conn):
	insert = {
		"name": s["pokemon"],
		"region": s["region"],
		"ability": s["ability"].replace("'", "''"),
		"tera_type": s["tera_type"],
		"nature": s["nature"]
	}
	if not pd.isnull(s["variant"]):
		insert["variant"] = s["variant"]
	if not pd.isnull(s["held_item"]):
		insert["held_item"] = s["held_item"].replace("'", "''")
	if not pd.isnull(s["regulation"]):
		insert["regulation"] = s["regulation"]

	ivs = {
		"attack_iv": s["attack_iv"],
		"special_attack_iv": s["special_attack_iv"],
		"speed_iv": s["speed_iv"]
	}

	insert["ivs"] = json.dumps(ivs)

	evs = {
			"hp_evs": s["hp_evs"],
			"attack_evs": s["attack_evs"],
			"defense_evs": s["defense_evs"],
			"special_attack_evs": s["special_attack_evs"],
			"special_defense_evs": s["special_defense_evs"],
			"speed_evs": s["speed_evs"]
	}

	insert["evs"] = json.dumps(evs)

	moves = []

	for move in ["move_1", "move_2", "move_3", "move_4"]:
		if not pd.isnull(s[move]):
			moves.append(s[move])

	if len(moves) == 0:
		raise Exception("competitive pokemon must have at least one move, but {} does not.".format(str(s["id"])))

	insert["moves"] = json.dumps(moves)

	columns = []
	values = []

	for key,value in insert.items():
		columns.append(key)
		values.append(str(value))


	conn.execute(text("INSERT INTO competitive_pokemon_lookup ({}) VALUES ({})".format(",".join(columns), "'" + "','".join(values) + "'")))


load_warehouse()







