from datetime import datetime
from annoy import AnnoyIndex

from defines.defines import METRIC_ANGULAR, VECTOR_DIMENSIONS
from memories.saving import save_memories
from paths.full_paths import (
    get_base_memories_full_path,
    get_base_memories_json_full_path,
)


class MemoriesDatabaseUpdater:
    """This class handles updating the vector and json database of an agent with new memories."""

    def __init__(
        self,
        agent_name: str,
        current_timestamp: datetime,
        new_memories: list[str],
        index: AnnoyIndex,
    ):
        self._agent_name = agent_name
        self._current_timestamp = current_timestamp
        self._new_memories = new_memories
        self._index = index

    def update(self):
        """Updates the corresponding vector and json databases with the new memories."""
        new_index = AnnoyIndex(VECTOR_DIMENSIONS, METRIC_ANGULAR)

        for i in range(self._index.get_n_items()):
            new_index.add_item(i, self._index.get_item_vector(i))

        # Vital to unload the original index, which should free up the database file.
        self._index.unload()

        try:
            save_memories(
                self._current_timestamp,
                self._new_memories,
                new_index,
                get_base_memories_full_path(self._agent_name),
                get_base_memories_json_full_path(self._agent_name),
            )
        finally:
            new_index.unload()
