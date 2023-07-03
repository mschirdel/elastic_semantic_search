import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

# load the env file
load_dotenv(find_dotenv())

SRC_DIR = Path(__file__).parent.parent
PROJECT_DIR = SRC_DIR.parent
PYTHON_LOG_CONFIG = SRC_DIR / "utils" / "logging.yaml"

# retrieve the credentials
ES_PASSWORD = os.environ.get('ELASTIC_PASSWORD')
ES_USER = os.environ.get('ELASTIC_USER')
ES_PORT = os.environ.get('ES_PORT')
ES_HOST = "localhost"
ES_URL = f"https://{ES_HOST}:{ES_PORT}/"
ES_CA_CERTS = os.environ.get('ES_CERTS')

# embedding model
MPNET_EMBEDDING = "sentence-transformers/all-mpnet-base-v2"
MAIN_EMBEDDING = MPNET_EMBEDDING
