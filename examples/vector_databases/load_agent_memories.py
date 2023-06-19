#!/usr/bin/env python3

import argparse
from paths.full_paths import (
    get_base_memories_full_path,
    get_base_memories_json_full_path,
)

from vector_databases.database_loader import DatabaseLoader


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

    database_full_path = get_base_memories_full_path(args.agent_name)
    database_json_full_path = get_base_memories_json_full_path(args.agent_name)

    index, memories_raw_data = DatabaseLoader(
        args.agent_name, database_full_path, database_json_full_path
    ).load()

    print(memories_raw_data)

    index.unload()


if __name__ == "__main__":
    main()
