"""This module contains the definition of the class MemoriesDatabaseCreator.
"""
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
    """Handles the creation of an agent's memories (vector database and json file)"""

    def create_database(self, agent_name: str, current_timestamp: datetime):
        """
        Creates the database of memories (vector database and json file) for a named agent,
        according to the seed memories that already should exist.

        Args:
            agent_name (str): the name of the agent to whom the memories correspond.
            current_datetime (datetime): the timestamp with which the memories database will be initialized.

        Raises:
            FileNotFoundError: If the seed memories text file doesn't exist or if
            the base memories files don't exist.
        """
        base_memories_full_path = get_base_memories_full_path(agent_name)
        base_memories_json_full_path = get_base_memories_json_full_path(agent_name)
        seed_memories_full_path = get_seed_memories_full_path(agent_name)

        if self._are_base_files_missing(
            base_memories_full_path, base_memories_json_full_path
        ):
            seed_memories = self._load_and_verify_seed_memories(
                seed_memories_full_path, agent_name
            )

            self._create_vector_database_and_json_file(
                current_timestamp,
                base_memories_full_path,
                base_memories_json_full_path,
                seed_memories,
            )

    def _are_base_files_missing(
        self, base_memories_full_path: str, base_memories_json_full_path: str
    ) -> bool:
        """Checks if the base memory files are missing."""
        return not os.path.isfile(base_memories_full_path) and not os.path.isfile(
            base_memories_json_full_path
        )

    def _load_and_verify_seed_memories(
        self, seed_memories_full_path: str, agent_name: str
    ) -> list[str]:
        """Loads and verifies the seed memories."""
        if not os.path.isfile(seed_memories_full_path):
            error_message = f"While attempting to create a memories database for agent '{agent_name}', couldn't find the seed memories: {seed_memories_full_path}"
            raise FileNotFoundError(error_message)

        return self._load_seed_memories(seed_memories_full_path)

    def _load_seed_memories(self, seed_memories_full_path: str) -> list[str]:
        """
        Loads seed memories from a file.

        Args:
            seed_memories_full_path (str): the full path to the seed memories text file.

        Returns:
            list[str]: A list of seed memories.

        Raises:
            FileNotFoundError: If the seed memories file doesn't exist.
        """
        with open(seed_memories_full_path, "r", encoding="utf-8") as file:
            return [end_string_with_period(seed_memory.strip()) for seed_memory in file]

    def _create_vector_database_and_json_file(
        self,
        current_timestamp: datetime,
        base_memories_full_path: str,
        base_memories_json_full_path: str,
        seed_memories: list[str],
    ):
        """
        Creates the vector database and JSON file for the agent's memories.

        Args:
            current_timestamp (datetime): the timestamp with which the memories database will be initialized.
            base_memories_full_path (str): the full path to where the vector database file will be created.
            base_memories_json_full_path (str): the full path to where the json file associated to the memories will be created.
            seed_memories (list[str]): A list of seed memories.

        Raises:
            Any exceptions raised by save_memories() or AnnoyIndex.
        """
        new_index = AnnoyIndex(VECTOR_DIMENSIONS, METRIC_ANGULAR)

        try:
            save_memories(
                current_timestamp,
                seed_memories,
                new_index,
                base_memories_full_path,
                base_memories_json_full_path,
            )
        finally:
            # always make sure to unload the AnnoyIndex, even if an exception was raised.
            new_index.unload()
