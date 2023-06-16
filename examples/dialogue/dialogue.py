#!/usr/bin/env python3

from console_output.messages import output_colored_message
from dialogue.dialogue_handler import DialogueHandler
from errors import FileDoesntExistError
from files.existence import file_exists
from files.loading import load_text_file


def main():
    dialogue_context_path = "examples/dialogue/dialogue_context.txt"
    if not file_exists(dialogue_context_path):
        raise FileDoesntExistError(
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
        raise FileDoesntExistError(
            f"The example required the file {first_dialogue_line_path} to exist."
        )

    messages.append(
        {
            "role": "user",
            "content": load_text_file(first_dialogue_line_path),
        }
    )

    messages = DialogueHandler(messages).perform_dialogue()

    # print the messages
    for message in messages:
        output_colored_message("light_yellow", message["content"])


if __name__ == "__main__":
    main()
