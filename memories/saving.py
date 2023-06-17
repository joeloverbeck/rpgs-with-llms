from datetime import datetime
import json

from annoy import AnnoyIndex
from memories.creation import create_vector_database
from memories.jsonification import append_to_previous_json_memories_if_necessary
from memories.validation import ensure_parity_between_databases

from memories.vectorization import create_vectorized_memory


def save_memories_to_json_file_ensuring_parity(
    memories_json_full_path: str, memories: dict, new_index: AnnoyIndex
):
    # Save the memories dictionary to a json file.
    with open(memories_json_full_path, "w", encoding="utf8") as json_file:
        json.dump(memories, json_file)

    # ensure that there is parity between the length of both the json and the index database.
    with open(memories_json_full_path, "r", encoding="utf8") as json_file:
        ensure_parity_between_databases(json.load(json_file), new_index)


def save_memories(
    current_timestamp: datetime,
    new_memories: list[str],
    new_index: AnnoyIndex,
    memories_full_path: str,
    memories_json_full_path: str,
):
    memories = {}

    for memory_description in new_memories:
        vector_index, memory = create_vectorized_memory(
            memory_description, current_timestamp, new_index
        )

        memories.update({vector_index: memory})

    create_vector_database(memories_full_path, new_index)

    memories = append_to_previous_json_memories_if_necessary(
        memories_json_full_path, memories
    )

    save_memories_to_json_file_ensuring_parity(
        memories_json_full_path, memories, new_index
    )
