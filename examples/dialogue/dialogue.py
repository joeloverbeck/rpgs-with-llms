#!/usr/bin/env python3

from console_output.messages import output_colored_message
from dialogue.dialogue_handler import DialogueHandler
from files.existence import file_exists
from files.loading import load_text_file
from llms.api_requests import request_response_from_ai_model_with_functions


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

    messages = DialogueHandler(
        messages, request_response_from_ai_model_with_functions
    ).perform_dialogue()

    # print the messages
    for message in messages:
        output_colored_message("light_yellow", message["content"])


if __name__ == "__main__":
    main()
