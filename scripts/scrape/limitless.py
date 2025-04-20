from bs4 import BeautifulSoup
import csv
import json
import re






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
	







