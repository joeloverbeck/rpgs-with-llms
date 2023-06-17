#!/usr/bin/env python3


from memories.memories_database_loader import MemoriesDatabaseLoader


def main():
    agent_name = "Test"

    index, memories_raw_data = MemoriesDatabaseLoader(agent_name).load()

    print(memories_raw_data)

    index.unload()


if __name__ == "__main__":
    main()
