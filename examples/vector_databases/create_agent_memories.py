#!/usr/bin/env python3
import argparse
from datetime import datetime
from paths.full_paths import (
    get_base_memories_full_path,
    get_base_memories_json_full_path,
    get_seed_memories_full_path,
)

from vector_databases.database_creator import DatabaseCreator


def main():
    parser = argparse.ArgumentParser(
        description="Creates the memories database for an agent."
    )
    parser.add_argument(
        "agent_name",
        help="The name of the agent whose memories database will be created.",
    )

    args = parser.parse_args()

    if not args.agent_name:
        print("Error: The name of the agent cannot be empty.")
        return None

    current_timestamp = datetime(2023, 6, 6)

    memories_database_creator = DatabaseCreator()

    memories_database_creator.create_database(
        args.agent_name,
        current_timestamp,
        get_base_memories_full_path(args.agent_name),
        get_base_memories_json_full_path(args.agent_name),
        get_seed_memories_full_path(args.agent_name),
    )


if __name__ == "__main__":
    main()
