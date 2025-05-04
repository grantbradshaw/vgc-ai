from bs4 import BeautifulSoup
import csv
import json
import pprint
import re
import requests

pp = pprint.PrettyPrinter(indent=1)

def load_tournaments():
	with open("data/regulations.json") as regulation_infile:
		regulations = json.load(regulation_infile)

	with open("data/limitless.csv") as tournament_infile:
		tournament_reader = csv.reader(tournament_infile, delimiter=',')
		row_count = 0

		for row in tournament_reader:
			if row_count == 0:
				row_count += 1
			else:
				if row[0] not in regulations:
					raise Exception("Invalid regulation in row {}".format(str(row_count)))

				if not re.match(r'^https:\/\/play.limitlesstcg.com\/tournament\/[a-z0-9]{24}\/standings$',row[1]):
					raise Exception("In row {}, url is invalid".format(str(row_count)))

				scrape_tournament(row[1])

# this function assumes that a proper limitless url is being provided
def scrape_tournament(url):
	data = {"players": {}}

	# firstly, we want to scrape the main page for the tournament - the individual players, their records, and their team urls

	r = requests.get(url)
	soup = BeautifulSoup(r.text, 'html.parser')
	
	teams_div = soup.find_all("div", {"class": "standings completed"})
	if not len(teams_div) == 1:
		raise Exception("Could not properly find standings element for url {}".format(url))

	results = teams_div[0].find_all("tr")

	row_count = 0
	for result in results:
		if row_count == 0:
			row_count += 1
		else:
			result_data = result.find_all("td")
			name = result_data[1].get_text()
			record = result_data[4].get_text()
			team_url = result_data[8].a['href']

			if name not in data["players"]:
				data["players"][name] = {}
				data["players"][name]["placement"] = row_count

				drop = "drop" in record
				record = record.replace("drop", "")
				record_list = record.split("-")

				data["players"][name]["record"] = {"drop": drop,
												   "wins": record_list[0].strip(),
												   "losses": record_list[1].strip(),
												   "draws": record_list[2].strip()}
				data["players"][name]["team_url"] = "https://play.limitlesstcg.com" + team_url

			else:
				raise Exception("Handling multiple players with same name not currently supported, raised for url {}".format(url))

		row_count += 1

	# next, we want to scrape the actual teams themselves

	for player in list(data["players"].keys()):
		scrape_team(data["players"][player]["team_url"])
		break


def scrape_team(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.text, 'html.parser')

	teamlist_div = soup.find_all("div", {"class": "teamlist-pokemon"})
	if not len(teamlist_div) == 1:
		raise Exception("Could not properly find teamlist div for url {}".format(url))

	team = teamlist_div[0].find_all("div", {"class": "pkmn"})
	if not len(team) == 6:
		raise Exception("Did not find expected 6 pokemon for url {}".format(url))

	for pokemon in team:
		name = pokemon.find("div", {"class": "name"}).get_text()
		item = pokemon.find("div", {"class": "item"}).get_text()
		ability = pokemon.find("div", {"class": "ability"}).get_text().replace("Ability:", "").strip()
		tera = pokemon.find("div", {"class": "tera"}).get_text().replace("Tera Type:", "").strip()

		moves = []
		for move in pokemon.find("ul", {"class": "attacks"}).find_all("li"):
			moves.append(move.get_text())

		print(name)
		print(item)
		print(ability)
		print(tera)
		print(moves)
		print("----")

	pokemon_list = teamlist_div[0]



load_tournaments()