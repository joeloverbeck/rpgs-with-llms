from datetime import datetime
import os

from annoy import AnnoyIndex
from defines.defines import METRIC_ANGULAR, VECTOR_DIMENSIONS
from memories.saving import save_memories

from paths.full_paths import (
    get_base_memories_full_path,
    get_base_memories_json_full_path,
    get_seed_memories_full_path,
)
from string_utils import end_string_with_period


class MemoriesDatabaseCreator:
    def __init__(self, agent_name: str, current_timestamp: datetime):
        self._agent_name = agent_name
        self._current_timestamp = current_timestamp

    def create_database(self):
        """Creates the database of memories (vector database and json file) for a named agent,
        according to the seed memories that already should exist.

        Raises:
            FileNotFoundError: if the seed memories text file doesn't exist.
        """
        base_memories_full_path = get_base_memories_full_path(self._agent_name)
        base_memories_json_full_path = get_base_memories_json_full_path(
            self._agent_name
        )
        seed_memories_full_path = get_seed_memories_full_path(self._agent_name)

        if not os.path.isfile(base_memories_full_path) and not os.path.isfile(
            base_memories_json_full_path
        ):
            # must create the memory files from the seed memories.
            if not os.path.isfile(seed_memories_full_path):
                error_message = f"While attempting to create a memories database for agent '{self._agent_name}', couldn't find the seed memories: {seed_memories_full_path}"
                raise FileNotFoundError(error_message)

            # at this point the file of seed memories exist, so we must load that file
            # and create the memories
            self._create_vector_database_and_json_file(self._load_seed_memories())

    def _load_seed_memories(self):
        seed_memories_full_path = get_seed_memories_full_path(self._agent_name)

        with open(seed_memories_full_path, "r", encoding="utf-8") as file:
            return [end_string_with_period(seed_memory.strip()) for seed_memory in file]

    def _create_vector_database_and_json_file(self, seed_memories: list[str]):
        new_index = AnnoyIndex(VECTOR_DIMENSIONS, METRIC_ANGULAR)

        base_memories_full_path = get_base_memories_full_path(self._agent_name)
        base_memories_json_full_path = get_base_memories_json_full_path(
            self._agent_name
        )

        save_memories(
            self._current_timestamp,
            seed_memories,
            new_index,
            base_memories_full_path,
            base_memories_json_full_path,
        )

        # always make sure to unload the AnnoyIndex.
        new_index.unload()
