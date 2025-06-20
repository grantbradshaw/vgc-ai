from bs4 import BeautifulSoup
import requests

def get_moves(pokemon, variant=None):
	url = "https://bulbapedia.bulbagarden.net/wiki/" + pokemon + "_(Pokémon)"
	r = requests.get(url)
	soup = BeautifulSoup(r.text, 'html.parser')

	moves = {}

	if variant:
		# we assume that the h5 element is where the regional variant information is stored, if present

		# firstly, we look for the h5 element underneath the "By leveling up" containing span
		# this gives us the id index for the relevant h5

		level_up_index = None

		for name_tag in soup.find_all("h5"):
			# one previous_sibling returns whitespace, as expected per Beautiful Soup docs
			header_candidate = name_tag.previous_sibling.previous_sibling

			if header_candidate.find("span", id="By_leveling_up"):
				if level_up_index is not None:
					raise Exception("Cannot overwrite Pokemon index")
				level_up_index = int(name_tag.find("span")["id"].split("_")[-1])

		# now, we find all h5 elements with the appropriate indices for the three types of moves
		# we assume that level_up_index + 1 is tm moves, level_up_index + 2 is breeding

		for name_tag in soup.find_all("h5"):
			if name_tag.find("span")["id"].split("_")[-1] == str(level_up_index):
				pokemon_name = name_tag.find("span").get_text().strip()
				moves[pokemon_name] = []

				level_up_moves_table = name_tag.find_next("table").find_next("tbody")
				level_up_moves_table = level_up_moves_table.find("span", text="Level").parent.parent.parent.parent.parent.find("tbody")
				level_up_moves = level_up_moves_table.find_all("tr")
				for move in level_up_moves:
					# this is the header of the table, but appears in tbody (despite the examination of the page suggesting otherwise)
					if move.find(title="Level") != None:
						continue
					
					move_name = move.find_all("td")[1].get_text().strip()
					if move_name not in moves[pokemon_name]:
						moves[pokemon_name].append(move_name)

			elif name_tag.find("span")["id"].split("_")[-1] == str(level_up_index + 1):
				pokemon_name = name_tag.find("span").get_text().strip()

				tm_moves_table = name_tag.find_next("table").find_next("tbody")
				tm_moves_table = tm_moves_table.find("span", text="TM").parent.parent.parent.parent.parent

				empty_table = False
				for th in tm_moves_table.find_all("th"):
					# we can't find("th", text="....") because there is whitespace
					if th.get_text().strip() == "This Pokémon learns no moves by TM.":
						empty_table = True

				if not empty_table:
					tm_moves = tm_moves_table.find("tbody").find_all("tr")
					for move in tm_moves:
						# this is the header of the table, but appears in tbody (despite the examination of the page suggesting otherwise)
						if move.find(title="TM") != None:
							continue

						move_name = move.find_all("td")[2].get_text().strip()
						if move_name not in moves[pokemon_name]:
							moves[pokemon_name].append(move_name)

			elif name_tag.find("span")["id"].split("_")[-1] == str(level_up_index + 2):
				pokemon_name = name_tag.find("span").get_text().strip()

				breeding_moves_table = name_tag.find_next("table").find_next("tbody")
				breeding_moves_table = breeding_moves_table.find("span", text="Parent").parent.parent.parent.parent.parent

				empty_table = False
				for th in breeding_moves_table.find_all("th"):
					# we can't find("th", text="....") because there is whitespace
					if th.get_text().strip() == "This Pokémon learns no moves by breeding.":
						empty_table = True

				if not empty_table:
					if breeding_moves_table.find("tbody").find("th", text="This Pokémon learns no moves by breeding.") == None:
						breeding_moves = breeding_moves_table.find_all("tr")
						for move in breeding_moves:

							# this is the header of the table, but appears in tbody (despite the examination of the page suggesting otherwise)
							if move.find(title="Pokémon Breeding") != None:
								continue

							move_name = move.find_all("td")[1].get_text().strip()
							if move_name not in moves[pokemon_name]:
								moves[pokemon_name].append(move_name)

	else:
		moves[pokemon] = []

		level_up_moves_table = soup.find(id="By_leveling_up").parent.find_next("table").find_next("tbody")
		level_up_moves_table = level_up_moves_table.find("span", text="Level").parent.parent.parent.parent.parent.find("tbody")
		level_up_moves = level_up_moves_table.find_all("tr")
		for move in level_up_moves:
			# this is the header of the table, but appears in tbody (despite the examination of the page suggesting otherwise)
			if move.find(title="Level") != None:
				continue
			
			move_name = move.find_all("td")[1].get_text().strip()
			if move_name not in moves[pokemon]:
				moves[pokemon].append(move_name)

		tm_moves_table = soup.find(id="By_TM").parent.find_next("table").find_next("tbody")
		tm_moves_table = tm_moves_table.find("span", text="TM").parent.parent.parent.parent.parent

		empty_table = False
		for th in tm_moves_table.find_all("th"):
			# we can't find("th", text="....") because there is whitespace
			if th.get_text().strip() == "This Pokémon learns no moves by TM.":
				empty_table = True

		if not empty_table:
			tm_moves = tm_moves_table.find("tbody").find_all("tr")
			for move in tm_moves:
				# this is the header of the table, but appears in tbody (despite the examination of the page suggesting otherwise)
				if move.find(title="TM") != None:
					continue

				move_name = move.find_all("td")[2].get_text().strip()
				if move_name not in moves[pokemon]:
					moves[pokemon].append(move_name)

		breeding_moves_table = soup.find(id="By_breeding").parent.find_next("table").find_next("tbody")
		breeding_moves_table = breeding_moves_table.find("span", text="Parent").parent.parent.parent.parent.parent

		empty_table = False
		for th in breeding_moves_table.find_all("th"):
			# we can't find("th", text="....") because there is whitespace
			if th.get_text().strip() == "This Pokémon learns no moves by breeding.":
				empty_table = True

		if not empty_table:
			if breeding_moves_table.find("tbody").find("th", text="This Pokémon learns no moves by breeding.") == None:
				breeding_moves = breeding_moves_table.find_all("tr")
				for move in breeding_moves:

					# this is the header of the table, but appears in tbody (despite the examination of the page suggesting otherwise)
					if move.find(title="Pokémon Breeding") != None:
						continue

					move_name = move.find_all("td")[1].get_text().strip()
					if move_name not in moves[pokemon]:
						moves[pokemon].append(move_name)
		
	print(moves)
