# Initialization
- python3 -m venv vgc-ai-env
- Can run schema.sql directly in your database. 
- Currently only written to run on local. Add a .env file with the appropriate environment variables
- Rename `data/ladder_dump_public.csv` to `data/ladder_dump.csv` (my personal file used includes teams that are not publicly available)

## Executing Code
All code is intended to be executed from root. Use `python3 -m scripts.load_raw_data` (for instance) to execute scripts directly.

## Database Structure
The intention of this project is to mock a production database / business intelligence data warehouse design. For technical simplicity, all tables cohabitate the same database, but the differing table implementations reflect the different types of tables (for instance, the presence of foreign keys in the production tables).

This project is designed to work with Postgres.

## Raw Data
All data is accurate for generation 9. The files in `data/` are manually transcribed by Bulbapedia. Some involve discretion (particularly with filtering) - for instance `data/held_items.json` only includes held items that I'm aware have seen competitive use or I believe might have an application.

## Future Work
- "Production" Database
	- Fill out details of moves & create a many to many table to reflect learnsets of Pokemon.
- Create a table to reflect thfe actual set of legal Pokemon in each regulation.
- Put together a table of trainers, so teams can be properly attributed
- Support Open Team Sheet pastes
- Record Pokemon genders
- Currently validation that data loading scripts are working properly is being done manually with direct SQL queries - would be better to add automated data validation checks
- Proper testing of various functions beyond the manual testing done by myself
- Better validation of resources allowed to be inserted in to the database
- Add support for regulation G (code has not been rigorously tested against regulation G pastes - i.e. Calyrex is known to error with the Ability scraped from Pastes)

## References
- Bulbapedia, under https://bulbapedia.bulbagarden.net/wiki/Bulbapedia:Copyrights