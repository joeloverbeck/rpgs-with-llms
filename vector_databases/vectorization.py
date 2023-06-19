from datetime import datetime

from annoy import AnnoyIndex

from defines.defines import MODEL
from llms.gpt_responder import GPTResponder
from vector_databases.jsonification import create_memory_dictionary


def create_vectorized_memory(
    memory_description: str,
    current_timestamp: datetime,
    index: AnnoyIndex,
):
    """Creates a vectorized memory of a memory description

    Args:
        memory_description (str): the description of the memory, in natural English
        current_timestamp (datetime): the current timestamp
        index (AnnoyIndex): the index of the 'annoy' library

    Returns:
        AnnoyIndex, dict: the index of the vector database, as well as a dict with the json-ready data of the memory
    """
    vector_index = index.get_n_items()

    index.add_item(vector_index, MODEL.encode(memory_description))

    memory = create_memory_dictionary(
        memory_description, current_timestamp, GPTResponder()
    )

    return vector_index, memory
