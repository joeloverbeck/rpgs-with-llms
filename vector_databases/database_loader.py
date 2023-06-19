import json
from annoy import AnnoyIndex
from defines.defines import METRIC_ANGULAR, VECTOR_DIMENSIONS
from vector_databases.jsonification import format_json_memory_data_for_python
from vector_databases.validation import ensure_parity_between_databases


class DatabaseLoader:
    def __init__(self, database_name, database_full_path, database_json_full_path):
        self._database_name = database_name

        self._database_full_path = database_full_path
        self._database_json_full_path = database_json_full_path

    def load(self):
        """Loads a vector database, whose name we already have.

        Raises:
            FileNotFoundError: if the vector database doesn't exist.

        Returns:
            AnnoyIndex, dict: the AnnoyIndex with the content of the vector database, along with the paired data in json format.
        """
        index = AnnoyIndex(VECTOR_DIMENSIONS, METRIC_ANGULAR)

        try:
            index.load(self._database_full_path)
        except OSError as exception:
            raise FileNotFoundError(
                f"Failed to load the index of a vector database because the file doesn't seem to exist. The filename is '{self._database_full_path}'. Error: {exception}"
            ) from exception

        with open(self._database_json_full_path, "r", encoding="utf8") as json_file:
            memories_raw_data = json.load(json_file)

        ensure_parity_between_databases(memories_raw_data, index)

        # Note: the timestamps stored in the JSON are strings. We need to convert them to proper timestamps
        memories_raw_data = format_json_memory_data_for_python(memories_raw_data)

        return index, memories_raw_data
