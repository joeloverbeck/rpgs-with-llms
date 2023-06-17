#!/usr/bin/env python3
import argparse
from datetime import datetime

from character_summaries.character_summary_creator import CharacterSummaryCreator


def main():
    parser = argparse.ArgumentParser(
        description="Creates the character summary of an agent."
    )
    parser.add_argument(
        "agent_name",
        help="The name of the agent whose character summary will be created.",
    )

    args = parser.parse_args()

    if not args.agent_name:
        print("Error: The name of the agent cannot be empty.")
        return None

    current_timestamp = datetime(2023, 6, 6)

    CharacterSummaryCreator(args.agent_name, current_timestamp).create()


if __name__ == "__main__":
    main()
