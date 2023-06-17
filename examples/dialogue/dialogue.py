#!/usr/bin/env python3
from datetime import datetime
from agents.agent import Agent
from console_output.messages import output_colored_message
from dialogue.dialogue_handler import DialogueHandler
from files.existence import file_exists
from files.loading import load_text_file
from llms.api_requests import request_response_from_ai_model_with_functions
from llms.user_requests import request_response_from_user


def main():
    dialogue_context_path = "examples/dialogue/dialogue_context.txt"
    if not file_exists(dialogue_context_path):
        raise FileNotFoundError(
            f"The example required the file {dialogue_context_path} to exist."
        )

    messages = []
    messages.append(
        {
            "role": "user",
            "content": load_text_file(dialogue_context_path),
        }
    )

    first_dialogue_line_path = "examples/dialogue/first_dialogue_line.txt"
    if not file_exists(first_dialogue_line_path):
        raise FileNotFoundError(
            f"The example required the file {first_dialogue_line_path} to exist."
        )

    messages.append(
        {
            "role": "user",
            "content": f"Continue the dialogue, starting with the following line:\n{load_text_file(first_dialogue_line_path)}",
        }
    )

    current_timestamp = datetime(2023, 11, 4, 19, 10)

    involved_agents = []

    leire = Agent("Leire", request_response_from_user)
    leire.set_status(
        "Leire was working overtime in the office, until Alberto the blob came down from another dimension to bother her."
    )

    involved_agents.append(leire)

    alberto = Agent("Alberto", request_response_from_ai_model_with_functions)
    alberto.set_status(
        "Alberto came down from a higher dimension to convince Leire to listen to his warning, so she can save humanity and the universe."
    )

    involved_agents.append(alberto)

    messages = DialogueHandler(
        involved_agents,
        leire,
        "Alberto is trying to convince Leire to save the universe, but Leire is reluctant because she doesn't even like people.",
        current_timestamp,
        request_response_from_ai_model_with_functions,
    ).perform_dialogue()

    # print the messages
    for message in messages:
        output_colored_message("light_yellow", message["content"])


if __name__ == "__main__":
    main()
