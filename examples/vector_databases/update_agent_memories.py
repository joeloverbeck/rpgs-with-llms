#!/usr/bin/env python3
import argparse

from datetime import datetime
from paths.full_paths import (
    get_base_memories_full_path,
    get_base_memories_json_full_path,
)
from vector_databases.database_loader import DatabaseLoader
from vector_databases.database_updater import DatabaseUpdater


def main():
    parser = argparse.ArgumentParser(
        description="Updates the memories database for an agent."
    )
    parser.add_argument(
        "agent_name",
        help="The name of the agent whose memories database will be updated with a new memory.",
    )
    parser.add_argument(
        "new_memory",
        help="The new memory that will be added to the memories database of the agent.",
    )

    args = parser.parse_args()

    if not args.agent_name:
        print("Error: The name of the agent cannot be empty.")
        return None
    if not args.new_memory:
        print("Error: The new memory cannot be empty.")
        return None

    database_full_path = get_base_memories_full_path(args.agent_name)
    database_json_full_path = get_base_memories_json_full_path(args.agent_name)

    index, _ = DatabaseLoader(
        args.agent_name, database_full_path, database_json_full_path
    ).load()

    current_timestamp = datetime(2023, 6, 6)

    DatabaseUpdater(
        current_timestamp,
        database_full_path,
        database_json_full_path,
    ).update_database_with_new_entries([args.new_memory], index)

    index.unload()


if __name__ == "__main__":
    main()
