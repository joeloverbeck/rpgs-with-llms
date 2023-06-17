#!/usr/bin/env python3
import argparse
from datetime import datetime

from memories.memories_database_creator import MemoriesDatabaseCreator


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

    memories_database_creator = MemoriesDatabaseCreator()

    memories_database_creator.create_database(args.agent_name, current_timestamp)


if __name__ == "__main__":
    main()
