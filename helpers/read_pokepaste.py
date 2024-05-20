from bs4 import BeautifulSoup
import requests

def get_pokemon_name_item_variant_region(s):
	if "@" in s:
		name_chunk, item_chunk = s.split("@")
	else:
		name_chunk, item_chunk = s, None

	# We currently don't care what gender a Pokemon is, so we strip this data for simplicity
	# PokePaste behaves strangely with forced gender Pokemon
	name_chunk = name_chunk.replace("(F)", "")
	name_chunk = name_chunk.replace("(M)", "")

	# For Pokemon with identical variants except for aesthetics, manually force them to the harmonized name in the raw data
	if "Gastrodon" in name_chunk:
		name_chunk = "Gastrodon"
	elif "Shellos" in name_chunk:
		name_chunk = "Shellos"
	elif "Vivillon" in name_chunk:
		name_chunk = "Vivillon"
	elif "Sinistcha" in name_chunk:
		name_chunk = "Sinistcha"
	elif "Polteageist" in name_chunk:
		name_chunk = "Polteageist"
	
	# if Pokemon are nicknamed, they are in the form "Brent (Okidogi)" [Nickname (Pokemon Name)]
	# we only care about the value in the parentheses, and have dealt with the other case where parentheses are present (gender)
	if "(" in name_chunk:
		name = name_chunk.split("(")[1].replace(")", "").strip()
	else:
		name = name_chunk.strip()

	if item_chunk:
		item = item_chunk.strip()
	else:
		item = None

	variant = None
	region = None

	# as regional variants were first introduced in Alola, "variants" from previous regions are not denoted with their region
	# i.e. Galarian Slowpoke is "Slowpoke-Galar" and Kantonian Slowpoke is "Slowpoke"
	regions = ["Alola", "Galar", "Paldea", "Hisui"]

	for region_name in regions:
		region_name_str = "-" + region_name
		if region_name_str in name:
			region = region_name
			name = name.replace(region_name_str, "")

	variant_map = {
		"10%": "10 Percent",
		"F": "Female",
		"M": "Male",
		"Combat": "Combat",
		"Aqua": "Aqua",
		"Blaze": "Blaze",
		"Attack": "Attack",
		"Defense": "Defense",
		"Speed": "Speed",
		"Sandy": "Sandy",
		"Trash": "Trash",
		"Heat": "Heat",
		"Wash": "Wash",
		"Frost": "Frost",
		"Fan": "Fan",
		"Mow": "Mow",
		"Origin": "Origin",
		"Sky": "Sky",
		"Blue-Striped": "Blue Striped",
		"White-Striped": "White Striped",
		"Therian": "Therian",
		"Black": "Black",
		"White": "White",
		"Small": "Small",
		"Large": "Large",
		"Super": "Super",
		"Unbound": "Unbound",
		"Pa'u": "Pa'u",
		"Pom-Pom": "Pom-Pom",
		"Sensu": "Sensu",
		"Midnight": "Midnight",
		"Dusk": "Dusk",
		"Dawn-Wings": "Dawn Wings",
		"Dusk-Mane": "Dusk Mane",
		"Low-Key": "Low Key",
		"Rapid-Strike": "Rapid Strike",
		"Ice": "Ice Rider",
		"Shadow": "Shadow Rider",
		"Four": "Family of Four",
		"Blue": "Blue",
		"Yellow": "Yellow",
		"White": "White",
		"Droopy": "Droopy",
		"Stretchy": "Stretchy",
		"Three-Segment": "Three Segment",
		"Roaming": "Roaming",
		"Wellspring": "Wellspring",
		"Hearthflame": "Hearthflame",
		"Cornerstone": "Cornerstone",
		"Bloodmoon": "Bloodmoon"
	}
	# descend by length so something like Dusk doesn't front-run Dusk-Mane
	# because Pokemon can have hyphens in their names (i.e. Chien-Pao), this is the simplest solution, rather than splitting on "-"
	for key in sorted(list(variant_map.keys()), key=len, reverse=True):
		key_str = "-" + key
		if key_str in name:
			variant = variant_map[key]
			name = name.replace(key_str, "")
			break

	return name, item, variant, region

def get_pokemon_ability_tera_type(s):
	return s.split(":")[1].strip()

def get_pokemon_stat_investment(s, stat_type):
	# it is assumed that trainers will not want to minimize HP, Defense, or Special Defense in any case
	if stat_type == "IV":
		stats = {
				 "attack_iv": 31,
				 "special_attack_iv": 31,
				 "speed_iv": 31
		}
	elif stat_type == "EV":
		stats = {
				  "hp_evs": 0,
				  "attack_evs": 0,
				  "defense_evs": 0,
				  "special_attack_evs": 0,
				  "special_defense_evs": 0,
				  "speed_evs": 0
		}
	else: 
		raise Exception("get_pokemon_stat_investment only supports IV or EV argument")

	if s == "":
		return stats
	else:
		stat_list = s.split(":")[1].split("/")


	for stat_string in stat_list:
		stat = stat_string.strip().split(" ")[1]
		value = int(stat_string.strip().split(" ")[0])

		if stat_type == "IV":
			if stat == "Atk":
				stats["attack_iv"] = value
			elif stat == "SpA":
				stats["special_attack_iv"] = value
			elif stat == "Spe":
				stats["speed_iv"] = value
		elif stat_type == "EV":
			if stat == "HP":
				stats["hp_evs"] = value
			elif stat == "Atk":
				stats["attack_evs"] = value
			elif stat == "Def":
				stats["defense_evs"] = value
			elif stat == "SpA":
				stats["special_attack_evs"] = value
			elif stat == "SpD":
				stats["special_defense_evs"] = value
			elif stat == "Spe":
				stats["speed_evs"] = value
			else:
				raise Exception("Unexpected EV value {}".format(stat))

	return stats

def get_pokemon_nature(s):
	return s.replace("Nature", "").strip()	

def clean_pokemon_moves(l):
	if len(l) > 4:
		raise Exception("There cannot be more than 4 moves")
	elif len(l) < 1:
		raise Exception("There must be at least 1 move")
	else:
		return list(map(lambda x: x[2:].strip(), l))

def extract_paste(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.text, 'html.parser')

	is_ots = True
	if "EVs" in soup.getText():
		is_ots = False

	team = []

	for i in range(1,7):
		try:
			pokemon = soup.select('article:nth-of-type(' + str(i) + ')')[0].pre.getText().split("\n")
		except IndexError:
			raise Exception("Only pastes with 6 Pokemon are supported.")

		if is_ots:
			raise Exception("OTS not currently supported")
		else:
			name, item, variant, region = get_pokemon_name_item_variant_region(pokemon[0])
			ability = get_pokemon_ability_tera_type(list(filter(lambda x: "Ability:" in x, pokemon))[0])
			# Rockruff technically has 4 abilities, and so I treat it as a variant
			if name == "Rockruff" and ability == "Own Tempo":
				variant = "Own Tempo"
			tera_type = get_pokemon_ability_tera_type(list(filter(lambda x: "Tera Type" in x, pokemon))[0])
			evs = get_pokemon_stat_investment(list(filter(lambda x: "EVs" in x, pokemon))[0], "EV")
			nature = get_pokemon_nature(list(filter(lambda x: "Nature" in x, pokemon))[0])
			ivs_string = list(filter(lambda x: "IVs" in x, pokemon))
			# >= 1 is to handle possible future edge cases where "IVs" is in a move name
			if len(ivs_string) >= 1:
				ivs = get_pokemon_stat_investment(ivs_string[0], "IV")
			else:
				ivs = get_pokemon_stat_investment("", "IV")

			# pastes can use two different dash characters to lead moves
			moves = clean_pokemon_moves(list(filter(lambda x: x[0:2] == "- " or x[0:2] == "– ", pokemon)))

			pokemon_data = {
				"pokemon": name,
				"ability": ability,
				"tera_type": tera_type,
				"evs": evs,
				"ivs": ivs,
				"moves": moves
			}

			if item:
				pokemon_data["held_item"] = item

			if variant:
				pokemon_data["variant"] = variant

			if region:
				pokemon_data["region"] = region

			if nature:
				pokemon_data["nature"] = nature

			team.append(pokemon_data)

	return team