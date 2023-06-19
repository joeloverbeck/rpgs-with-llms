"""This module contains the definition of the class MemoriesDatabaseCreator.
"""
from datetime import datetime
import os
from typing import List

from annoy import AnnoyIndex
from defines.defines import METRIC_ANGULAR, VECTOR_DIMENSIONS
from vector_databases.saving import save_memories

from string_utils import end_string_with_period


class DatabaseCreator:
    """Handles the creation of a vector database (vector database and json file) based on a seed file."""

    def create_database(
        self,
        database_name: str,
        current_timestamp: datetime,
        vector_database_full_path: str,
        vector_database_json_full_path: str,
        seed_full_path: str,
    ):
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

        if self._are_base_files_missing(
            vector_database_full_path, vector_database_json_full_path
        ):
            seed_memories = self._verify_and_load_seeds(seed_full_path, database_name)

            self._create_vector_database_and_json_file(
                current_timestamp,
                vector_database_full_path,
                vector_database_json_full_path,
                seed_memories,
            )

    def _are_base_files_missing(
        self, base_memories_full_path: str, base_memories_json_full_path: str
    ) -> bool:
        """Checks if the base memory files are missing."""
        return not os.path.isfile(base_memories_full_path) and not os.path.isfile(
            base_memories_json_full_path
        )

    def _verify_and_load_seeds(
        self, seed_memories_full_path: str, database_name: str
    ) -> List[str]:
        """Loads and verifies the seed memories."""
        if not os.path.isfile(seed_memories_full_path):
            error_message = f"While attempting to create a vector database '{database_name}', couldn't find the seed file: {seed_memories_full_path}"
            raise FileNotFoundError(error_message)

        with open(seed_memories_full_path, "r", encoding="utf-8") as file:
            return [end_string_with_period(seed_memory.strip()) for seed_memory in file]

    def _create_vector_database_and_json_file(
        self,
        current_timestamp: datetime,
        base_memories_full_path: str,
        base_memories_json_full_path: str,
        seed_memories: List[str],
    ) -> None:
        """
        Creates the vector database and JSON file.

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
