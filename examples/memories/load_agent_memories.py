#!/usr/bin/env python3

import argparse

from memories.memories_database_loader import MemoriesDatabaseLoader


def main():
    parser = argparse.ArgumentParser(
        description="Loads the memories database for an agent."
    )
    parser.add_argument(
        "agent_name",
        help="The name of the agent whose memories database will be loaded.",
    )

    args = parser.parse_args()

    if not args.agent_name:
        print("Error: The name of the agent cannot be empty.")
        return None

    index, memories_raw_data = MemoriesDatabaseLoader(args.agent_name).load()

    print(memories_raw_data)

    index.unload()


if __name__ == "__main__":
    main()
