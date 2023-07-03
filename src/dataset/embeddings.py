import argparse
import os
import textwrap
import traceback

import argcomplete
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from src.utils import constants
from src.utils.logging import getLogger

# Instantiate the logger
logger = getLogger(__name__)


def local_text_embedding(
    client: Elasticsearch,
    index_name: str,
    data_path: str,
    model: SentenceTransformer = SentenceTransformer(constants.MAIN_EMBEDDING),
):
    """Read text files and embed them in the ES.

    Args:
        client (Elasticsearch): elasticsearch client
        index_name (str): index name defined in the elasticsearch
        data_path (str): the path for the folder containing the text file.
    """
    logger.info(f"Loaded sentence transformer {constants.MAIN_EMBEDDING} with default embedding")
    logger.info(f"Embedding dimensions : {model.get_sentence_embedding_dimension()}")
    for i, filename in enumerate(os.listdir(data_path)):
        # Check if the file is a text file
        if filename.endswith(".txt"):
            file_path = os.path.join(data_path, filename)
            with open(file_path, "r") as file:
                content = file.read()
                # Parse the file content here
                logger.debug(f"Embedding {filename}:")
                doc = {
                    "sentence_text": content,
                    "document_name": f"Document {i}",
                    "sentence_embedding": model.encode(content),
                }

                client.index(index=index_name, document=doc)


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
    parser.add_argument('--data_path', help='data path that contains documents.', type=str)
    parser.add_argument('--index_name', help='elasticsearch defined index.', type=str)
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    logger.info('Started invoking elasticsearch client.')
    # Create the client instance
    client = Elasticsearch(
        hosts=constants.ES_URL,
        ca_certs=constants.ES_CA_CERTS,
        basic_auth=(constants.ES_USER, constants.ES_PASSWORD),
    )
    # Get cluster information
    logger.info(client.info())

    # Run embedding
    try:
        logger.info("Running embeddings.")
        local_text_embedding(client=client, index_name=args.index_name, data_path=args.data_path)
    except Exception as e:
        logger.error(f"Could not perform the embedding due to error {e}")
        print(traceback.format_exc())
