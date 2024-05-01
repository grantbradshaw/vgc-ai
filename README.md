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

## References
- Bulbapedia, under https://bulbapedia.bulbagarden.net/wiki/Bulbapedia:Copyrights