#!/usr/bin/env python3

from datetime import datetime
from memories.memories_database_loader import MemoriesDatabaseLoader
from memories.memories_database_querier import MemoriesDatabaseQuerier


def main():
    agent_name = "Test"

    index, raw_memories_data = MemoriesDatabaseLoader(agent_name).load()

    current_timestamp = datetime(2023, 6, 7)

    query_1 = "Test's relationship with turds"

    query_results = MemoriesDatabaseQuerier(
        agent_name, current_timestamp, raw_memories_data, index
    ).query(query_1, 3)

    print(f"{query_1}:\n")
    for query_result in query_results:
        print(f" {query_result}")

    query_2 = "What is wrong with Test's brain"

    query_results = MemoriesDatabaseQuerier(
        agent_name, current_timestamp, raw_memories_data, index
    ).query(query_2, 3)

    print(f"{query_2}:\n")
    for query_result in query_results:
        print(f" {query_result}")

    index.unload()


if __name__ == "__main__":
    main()
