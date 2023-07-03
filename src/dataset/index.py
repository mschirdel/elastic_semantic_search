import argparse
import textwrap

import argcomplete
from elasticsearch import Elasticsearch

from src.utils import constants
from src.utils.logging import getLogger

# instantiate the logger
logger = getLogger(__name__)

if __name__ == "__main__":

    # get the parser arguments
    parser = argparse.ArgumentParser(
        description="script to run indexing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            ''''
        Current arguments are:

        --index_name="index0"
        --embedding_dims="512"

        Example Usage
        -------------
        python %(prog)s
        python %(prog)s --index_name=es0 --embedding_dims 512

        '''
        ),
    )
    parser.add_argument('--index_name', help='elasticsearch index name', type=str)
    parser.add_argument('--embedding_dims', help='text embedding vector dimension.', type=int)
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    logger.info('Started invoking elasticsearch client.')
    # Create the client instance
    client = Elasticsearch(
        hosts=constants.ES_URL,
        ca_certs=constants.ES_CA_CERTS,
        basic_auth=(constants.ES_USER, constants.ES_PASSWORD),
    )
    # get cluster information
    logger.info(client.info())

    # define index config
    settings = {"number_of_shards": 2, "number_of_replicas": 1}
    mappings = {
        "properties": {
            "sentence_embedding": {"type": "dense_vector", "dims": 12, "index": 12, "similarity": "cosine"},
            "sentence_text": {"type": "text", "fields": {"keyword": {"type": "text"}}},
            "document_name": {"type": "text", "fields": {"keyword": {"type": "text"}}},
        }
    }

    # create an index in elasticsearch
    try:
        client.indices.create(
            index=args.index_name,
            settings=settings,
            mappings=mappings,
        )
        logger.info(f"Built {args.index_name} index.")
    except Exception as e:
        logger.debug(f'Index "{args.index_name}" already exists')
