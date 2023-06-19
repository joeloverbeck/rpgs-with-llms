from datetime import datetime
from typing import List, Tuple
from annoy import AnnoyIndex

from defines.defines import DECAY_RATE, METRIC_ANGULAR, VECTOR_DIMENSIONS
from math_utils import calculate_recency
from vector_databases.database_entry import DatabaseEntry
from vector_databases.jsonification import format_python_memory_data_for_json
from vector_databases.saving import (
    save_memories,
    save_memories_to_json_file_ensuring_parity,
)


class DatabaseUpdater:
    """This class handles updating the vector and json of a vector database."""

    def __init__(
        self,
        current_timestamp: datetime,
        database_full_path: str,
        database_json_full_path: str,
    ):
        self._current_timestamp = current_timestamp
        self._database_full_path = database_full_path
        self._database_json_full_path = database_json_full_path

    def update_database_with_new_entries(
        self, new_entries: list[str], index: AnnoyIndex
    ):
        """Updates the corresponding vector and json databases with the new entries."""
        new_index = AnnoyIndex(VECTOR_DIMENSIONS, METRIC_ANGULAR)

        for i in range(index.get_n_items()):
            new_index.add_item(i, index.get_item_vector(i))

        # Vital to unload the original index, which should free up the database file.
        index.unload()

        try:
            save_memories(
                self._current_timestamp,
                new_entries,
                new_index,
                self._database_full_path,
                self._database_json_full_path,
            )
        finally:
            new_index.unload()

    def update_most_recent_access_timestamps(
        self,
        scores: List[Tuple[DatabaseEntry, float]],
        index: AnnoyIndex,
        raw_data: dict,
    ):
        """Updates the most recent access timestamps of query results.
        Note: it does not close the AnnoyIndex, because this is part of a repeatable query operation.

        Args:
            scores (List[Tuple[DatabaseEntry, float]]): a scored and ordered list of relevant results of a query.
            raw_data (dict): the entire raw data of the corresponding vector database.

        Returns:
            dict: the data in raw data format, with updated 'most_recent_access_timestamp' and 'recency' values.
        """

        # Update the 'most_recent_access_timestamp' as well as the 'recency' values of each entry
        for database_entry, _ in scores:
            raw_data[str(database_entry.get_index())]["recency"] = calculate_recency(
                self._current_timestamp,
                database_entry.get_most_recent_access_timestamp(),
                DECAY_RATE,
            )

            raw_data[str(database_entry.get_index())][
                "most_recent_access_timestamp"
            ] = self._current_timestamp.isoformat()

        # After we have modified the most 'recent_access_timestamp' values, we have to ensure
        # that we format the _raw_data into jsonificable values (meaning that we turn the dates into text.)
        raw_data = format_python_memory_data_for_json(raw_data)

        save_memories_to_json_file_ensuring_parity(
            self._database_json_full_path, raw_data, index
        )
