#!/usr/bin/env python3

from agents.agent import Agent
from console_output.messages import pretty_print_conversation
from defines.defines import GPT_4
from dialogue.dialogue_requester import DialogueRequester
from errors import FileDoesntExistError
from files.existence import file_exists
from files.loading import load_text_file
from input.confirmation import request_confirmation
from llms.api_requests import request_response_from_ai_model
from llms.user_requests import request_response_from_user


def main():
    messages = []

    system_content = "I am DialogueGPT. I have the responsibility of carrying on a dialogue between two or more characters until the context of "
    system_content += "the dialogue suggests that the dialogue should end."
    messages.append(
        {
            "role": "system",
            "content": system_content,
        }
    )

    dialogue_context_path = "examples/dialogue_context.txt"
    if not file_exists(dialogue_context_path):
        raise FileDoesntExistError(
            f"The example required the file {dialogue_context_path} to exist."
        )

    messages.append(
        {
            "role": "user",
            "content": load_text_file(dialogue_context_path),
        }
    )

    first_dialogue_line_path = "examples/first_dialogue_line.txt"
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

    functions = []
    functions.append(
        {
            "name": "stop_dialogue",
            "description": "Stops the current dialogue",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
    )

    agents = []
    agents.append(Agent("The Captain", request_response_from_user))

    last_speaker = None  # Initialize the last_speaker variable

    should_continue_dialogue = True

    while should_continue_dialogue:
        # Only request confirmation if the last speaker wasn't the user
        if last_speaker != "user" and request_confirmation(
            f"Last message: {messages[-1]['content']}\nDo you want to interject in the conversation?"
        ):
            request_function = request_response_from_user
        else:
            request_function = request_response_from_ai_model

        dialogue_requester = DialogueRequester(
            messages,
            functions,
            request_function,
            function_call="auto",
            model=GPT_4,
        )

        response = dialogue_requester.request_response()

        # Determine if the model has called the function to end the dialogue.
        message = response["choices"][0]["message"]

        # Update the last_speaker variable
        last_speaker = message.get("role")

        if message.get("function_call"):
            should_continue_dialogue = False

        else:
            messages.append(message)

    # print the messages
    pretty_print_conversation(messages)


if __name__ == "__main__":
    main()
