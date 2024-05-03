# VGC "AI"
Following in the tradition of websites such as [Pikalytics](https://www.pikalytics.com) and [LabMaus](http://labmaus.net/tournaments/1801), this project intends to continue on using data to improve at competitive Pokemon doubles (VGC). Playing VGC has a number of unique challenges,
- Metagames change quickly and frequently, making it difficult to keep up with how to position a team
- Within games and particularly when building teams, there are a dizzying number of options available, making optimal play and teambuilding extremely difficult.
- Similar to games like poker, it is often hard to disentangle after a loss (or win) how much the result can be attributed to luck vs. skill

There are two primary goals of this application to help address these issues. They are as follows,
- Build a robust database of competitive teams / pokemon spreads, both to use to attempt to predict developments in the metagame as well as find better jumping off points for building teams (the latter extends upon the existing work done by others in the community).
- Using a combination of game theory and ML, build a program that can evaluate a matchup between two teams, to leverage for post game review, team optimization, or at the extreme, even the development of new teams.

The current phase of the project is predominately data engineering - build the database that will be used for the project as a whole.

## Technical Notes
This project is developed in Python and intended to be used with a Postgres backend. Despite using a single database, the schema intention is to mimic a production / data warehouse model. The two types of tables should adhere to the "proper" data design needs of each type of database (for instance, the production tables will use foreign keys where warehouse tables will predominately not).

### Initialization
Currently, the project simply runs on local. To spin up this project on your own, simply follow these steps (after cloning this project),
- Set up a virtual environment, with a command such as `python3 -m venv vgc-ai-env`. Once you've sourced your virtual environment, `pip install -r requirements.txt` 
- Once you have set up a local postgres database, change `.env-example` to `.env` with the proper database environment variables. The assumption is that you do not have a password set, but if you do, you can update `helpers/establish_db_connection.py` to take a password
- Within your database, run the commands in `schema.sql`
- Before starting to seed the database, rename `data/ladder_dump_public.csv` to `data/ladder_dump.csv` (the file I use on local has private teams that I won't upload to Github)
- Finally, run `python3 -m scripts.load_raw_data` followed by `python3 -m scripts.load_competitive_pokemon`

### Data Notes
All data is accurate as of generation 9. The files in `data/` are all sourced from Bulbapedia, with the exception of data added afterwards while testing with actual teams. I used discretion in seeding some of the files, specifically `data/held_items.json` - I only included items I thought had any use in competitive.


## Future Work
- "Production" Database
	- Fill out details of moves & create a many to many table to reflect learnsets of Pokemon.
- Create a table to reflect the actual set of legal Pokemon in each regulation.
- Put together a table of trainers, so teams can be properly attributed.
- Support Open Team Sheet pastes.
- Record Pokemon genders.
- Currently validation that data loading scripts are working properly is being done manually with direct SQL queries - would be better to add automated data validation checks.
- Proper testing of various functions beyond the manual testing done by myself. 
- Better validation of data inserted in to the database. For instance, don't insert a competitive pokemon with an ability the Pokemon can't have, don't insert ill formatted resources
- Add support for regulation G (code has not been rigorously tested against regulation G pastes - i.e. Calyrex is known to error with the Ability scraped from Pastes).
- Support better "ETL" patterns for data warehouse - for instance, currently a bit of an anti-pattern (wipes table and full loads), but if we actually tracked changes, we could use better patterns (DELETE removed / updated rows, then INSERT the updated rows / new rows)
- Refactor scripts to use the `pd.read_sql` pattern used in `scripts/load_warehouse.py`

## References
- Bulbapedia, under this [License](https://bulbapedia.bulbagarden.net/wiki/Bulbapedia:Copyrights)

## License
- This code is provided under [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/)
- Pokemon names and other particulars of Pokemon games are the intellectual property of Nintendo. 

