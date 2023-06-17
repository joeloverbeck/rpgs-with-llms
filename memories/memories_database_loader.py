import json
from annoy import AnnoyIndex
from defines.defines import METRIC_ANGULAR, VECTOR_DIMENSIONS
from memories.jsonification import format_json_memory_data_for_python
from memories.validation import ensure_parity_between_databases
from paths.full_paths import (
    get_base_memories_full_path,
    get_base_memories_json_full_path,
)


class MemoriesDatabaseLoader:
    def __init__(self, agent_name):
        self._agent_name = agent_name

    def load(self):
        """Loads the memories of an agent, whose name we already have.

        Raises:
            FileNotFoundError: if the vector database doesn't exist.

        Returns:
            AnnoyIndex, dict: the AnnoyIndex with the content of the vector database, along with the paired memories in json format.
        """
        base_memories_full_path = get_base_memories_full_path(self._agent_name)
        base_memories_json_full_path = get_base_memories_json_full_path(
            self._agent_name
        )

        index = AnnoyIndex(VECTOR_DIMENSIONS, METRIC_ANGULAR)

        try:
            index.load(base_memories_full_path)
        except OSError as exception:
            raise FileNotFoundError(
                f"Failed to load the index of a vector database because the file doesn't seem to exist. The filename is '{base_memories_full_path}'. Error: {exception}"
            ) from exception

        with open(base_memories_json_full_path, "r", encoding="utf8") as json_file:
            memories_raw_data = json.load(json_file)

        ensure_parity_between_databases(memories_raw_data, index)

        # Note: the timestamps stored in the JSON are strings. We need to convert them to proper timestamps
        memories_raw_data = format_json_memory_data_for_python(memories_raw_data)

        return index, memories_raw_data
