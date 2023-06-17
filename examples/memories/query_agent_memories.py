#!/usr/bin/env python3
import argparse

from datetime import datetime
from memories.memories_database_loader import MemoriesDatabaseLoader
from memories.memories_database_querier import MemoriesDatabaseQuerier


def main():
    parser = argparse.ArgumentParser(
        description="Queries the memories database of an agent."
    )
    parser.add_argument(
        "agent_name",
        help="The name of the agent whose memories database will be queried.",
    )
    parser.add_argument(
        "query",
        help="The query for the agent's memories database.",
    )

    args = parser.parse_args()

    if not args.agent_name:
        print("Error: The name of the agent cannot be empty.")
        return None
    if not args.query:
        print("Error: The query cannot be empty.")
        return None

    index, raw_memories_data = MemoriesDatabaseLoader(args.agent_name).load()

    current_timestamp = datetime(2023, 6, 7)

    query_results = MemoriesDatabaseQuerier(
        args.agent_name, current_timestamp, raw_memories_data, index
    ).query(args.query, 5)

    print(f"{args.query}:\n")
    for query_result in query_results:
        print(f" {query_result}")

    index.unload()


if __name__ == "__main__":
    main()
