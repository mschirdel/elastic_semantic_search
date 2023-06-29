import os 
from dotenv import find_dotenv, load_dotenv

# load the env file 
load_dotenv(find_dotenv())

# retrieve the credentials 
ES_PASSWORD = os.environ.get('ES_PASSWORD')
ES_USER = os.environ.get('ES_USER')
ES_PORT = os.environ.get('ES_PORT')
ES_HOST = "localhost"
ES_URL = f"https://{ES_HOST}:{ES_PORT}/"
ES_CA_CERTS = os.environ.get('ES_CERTS')
