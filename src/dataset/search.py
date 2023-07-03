import argparse
import os
import readline
import textwrap
import traceback

import argcomplete
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from src.utils import constants
from src.utils.logging import getLogger

# Enable command history
readline.parse_and_bind("tab: complete")

# Instantiate the logger
logger = getLogger(__name__)

def perform_search(query: str,
                   client: Elasticsearch,
                   index_name: str,
                   model=SentenceTransformer(constants.MAIN_EMBEDDING)):
    # Perform transformations on the input query
    # Example transformation: Convert query to uppercase
    query_emb = model.encode(query)

    res = client.search(
        knn={
            "field": "sentence_embedding",
            "query_vector": query_emb,
            "k": 5,
            "num_candidates": 5
        },
        index=index_name,
    )

    # Generate results based on the search query
    results = [
        f'Result 1: {res["hits"]["hits"][0]["_source"]["sentence_text"]}',
        'score: {res["hits"]["hits"][0]["_score"]}',
        f'Result 2: {res["hits"]["hits"][1]["_source"]["sentence_text"]}',
        'score: {res["hits"]["hits"][1]["_score"]}',
        f'Result 3: {res["hits"]["hits"][2]["_source"]["sentence_text"]}',
        'score: {res["hits"]["hits"][2]["_score"]}'
    ]

    # Return the results
    return results

def clear_screen():
    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":

    # Get the parser arguments
    parser = argparse.ArgumentParser(
        description="script to run indexing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            ''''
        Current arguments are:

        --data_path="/data/sample_data"
        --index_name="es0"

        Example Usage
        -------------
        python %(prog)s
        python %(prog)s --data_path=/data/sample_data --index_name=es0

        '''
        ),
    )
    parser.add_argument('--index_name', help='elasticsearch defined index.', type=str)
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    logger.info('Started invoking elasticsearch client.')
    # Create the client instance
    client = Elasticsearch(
        hosts=constants.ES_URL,
        ca_certs=constants.ES_CA_CERTS,
        basic_auth=(constants.ES_USER, constants.ES_PASSWORD)
    )
    # Get cluster information
    logger.info(client.info())

    # Run embedding
    try:
        logger.info("Running search.")

        # Main search system CLI loop
        while True:
            # Accept input query from the command line
            query = input("Enter your query (or 'exit' to quit): ")

            # Check if the user wants to exit
            if query.lower() == "exit":
                print("Exiting...")
                break

            # Clear the terminal screen
            clear_screen()

            # Perform the search and get the results
            results = perform_search(query, client=client, index_name=args.index_name)

            # Print the results
            print("Results:")
            for result in results:
                print(result)
            print()

            # Prompt the user to press Enter to continue
            input("Press Enter to continue...")
            clear_screen()
    except Exception as e:
        logger.error(f"Could not perform the embedding due to error {e}")
        print(traceback.format_exc())
