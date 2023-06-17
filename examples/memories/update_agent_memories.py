#!/usr/bin/env python3
import argparse

from datetime import datetime
from memories.memories_database_loader import MemoriesDatabaseLoader
from memories.memories_database_updater import MemoriesDatabaseUpdater


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

    index, _ = MemoriesDatabaseLoader(args.agent_name).load()

    current_timestamp = datetime(2023, 6, 6)

    MemoriesDatabaseUpdater(
        args.agent_name, current_timestamp, [args.new_memory], index
    ).update()

    index.unload()


if __name__ == "__main__":
    main()
