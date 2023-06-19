#!/usr/bin/env python3
import argparse

from datetime import datetime
from paths.full_paths import (
    get_base_memories_full_path,
    get_base_memories_json_full_path,
)
from vector_databases.database_loader import DatabaseLoader
from vector_databases.database_querier import DatabaseQuerier
from vector_databases.database_updater import DatabaseUpdater


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

    database_full_path = get_base_memories_full_path(args.agent_name)
    database_json_full_path = get_base_memories_json_full_path(args.agent_name)

    index, raw_memories_data = DatabaseLoader(
        args.agent_name, database_full_path, database_json_full_path
    ).load()

    current_timestamp = datetime(2023, 6, 7)

    database_updater = DatabaseUpdater(
        current_timestamp, database_full_path, database_json_full_path
    )

    query_results = DatabaseQuerier(
        current_timestamp,
        raw_memories_data,
        index,
        database_full_path,
        database_json_full_path,
        database_updater,
    ).query(args.query, 5)

    print(f"{args.query}:\n")
    for query_result in query_results:
        print(f" {query_result}")

    index.unload()


if __name__ == "__main__":
    main()
