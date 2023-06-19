#!/usr/bin/env python3
import argparse
from datetime import datetime
import os

from paths.full_paths import (
    get_seed_facts_of_simulation_full_path,
    get_simulation_facts_full_path,
    get_simulation_facts_json_full_path,
)
from vector_databases.database_creator import DatabaseCreator


def main():
    parser = argparse.ArgumentParser(description="Creates a simulation.")
    parser.add_argument(
        "simulation_name",
        help="The name of the simulation that will be created.",
    )

    args = parser.parse_args()

    if not args.simulation_name:
        print("Error: The name of the simulation cannot be empty.")
        return None

    # The seed facts of the simulation need to be turned into a vector database.
    seed_facts_of_simulation_full_path = get_seed_facts_of_simulation_full_path(
        args.simulation_name
    )

    if not os.path.isfile(seed_facts_of_simulation_full_path):
        print(
            f"The seed facts for the simulation '{args.simulation_name}' need to exist at '{seed_facts_of_simulation_full_path}'"
        )
        return None

    # Must create the corresponding vector database from those seed facts.

    # This function should create the json file corresponding to the simulation.
    current_timestamp = datetime(2023, 6, 19, 9, 0, 0)

    facts_database_creator = DatabaseCreator()

    facts_database_creator.create_database(
        args.simulation_name,
        current_timestamp,
        get_simulation_facts_full_path(args.simulation_name),
        get_simulation_facts_json_full_path(args.simulation_name),
        get_seed_facts_of_simulation_full_path(args.simulation_name),
    )


if __name__ == "__main__":
    main()
