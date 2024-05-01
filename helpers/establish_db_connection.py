from dotenv import load_dotenv
import os
import sqlalchemy as db

def get_db_engine():
	load_dotenv()
	engine = db.create_engine("postgresql+psycopg2://{}:@{}:{}/{}".format(os.environ["user"], os.environ["host"], os.environ["port"], os.environ["database"]))
	return engine


