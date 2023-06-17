#!/usr/bin/env python3

from datetime import datetime
from memories.memories_database_loader import MemoriesDatabaseLoader
from memories.memories_database_updater import MemoriesDatabaseUpdater


def main():
    agent_name = "Test"

    index, _ = MemoriesDatabaseLoader(agent_name).load()

    new_memory = input(f"Write new memory for agent '{agent_name}': ")

    current_timestamp = datetime(2023, 6, 6)

    MemoriesDatabaseUpdater(agent_name, current_timestamp, [new_memory], index).update()

    index.unload()


if __name__ == "__main__":
    main()
