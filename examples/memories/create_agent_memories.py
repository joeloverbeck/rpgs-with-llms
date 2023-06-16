#!/usr/bin/env python3

from datetime import datetime

from memories.memories_database_creator import MemoriesDatabaseCreator


def main():
    agent_name = "Test"

    current_timestamp = datetime(2023, 6, 6)

    memories_database_creator = MemoriesDatabaseCreator()

    memories_database_creator.create_database(agent_name, current_timestamp)


if __name__ == "__main__":
    main()
