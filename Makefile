.PHONY: clean run_precommit copy_cert index embedding search

PWD := $(shell pwd)
INDEX_NAME="test-0"
EMBEDDING_DIMS=768
DATA_PATH="${PWD}/data/sample_data"
PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))



# Delete all compiled python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

# Pre commit check
run_precommit:
	pre-commit run --all-files

# Elasticsearch cert local copy
copy_cert:
	docker cp elastic_semantic_search_es01_1:/usr/share/elasticsearch/config/certs/ca/ca.crt ~/.creds

# Make index in elasticsearch
index:
	PYTHONPATH="." poetry run python ./src/dataset/index.py \
				--index_name $(INDEX_NAME) \
				--embedding_dims $(EMBEDDING_DIMS)

# Make document embedding in elasticsearch
embedding:
	PYTHONPATH="." poetry run python ./src/dataset/embeddings.py \
				--index_name $(INDEX_NAME) \
				--data_path $(DATA_PATH)

# Run search from elasticsearch
search:
	PYTHONPATH="." poetry run python ./src/dataset/search.py \
				--index_name $(INDEX_NAME)
