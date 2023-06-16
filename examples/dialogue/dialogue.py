#!/usr/bin/env python3

import json
from console_output.messages import output_colored_message
from defines.defines import GPT_4
from errors import FileDoesntExistError
from files.existence import file_exists
from files.loading import load_text_file
from input.confirmation import request_confirmation
from llms.api_requests import request_response_from_ai_model_with_functions
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

    dialogue_context_path = "examples/dialogue/dialogue_context.txt"
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

    functions = []
    functions.append(
        {
            "name": "stop_dialogue",
            "description": "Stops the dialogue if the latest utterances make it likely that the dialogue should end now.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
    )
    functions.append(
        {
            "name": "get_lines_of_dialogue",
            "description": "Gets the lines of dialogue for the characters that realistically would speak at this point of the dialogue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lines_of_dialogue": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": """A line of dialogue, starting with the name of the character, followed by a colon and the spoken line of dialogue.
                             Can also include narration in parenthesis, if necessary.""",
                        },
                    }
                },
                "required": ["lines_of_dialogue"],
            },
        }
    )

    user_spoke_last = False  # Initialize the last_speaker variable

    should_continue_dialogue = True

    while should_continue_dialogue:
        # Only request confirmation if the last speaker wasn't the user
        if not user_spoke_last and request_confirmation(
            "Last 3 messages: \n"
            + "\n".join([msg["content"] for msg in messages[-3:]])
            + "\nDo you want to interject in the conversation?"
        ):
            request_function = request_response_from_user
        else:
            request_function = request_response_from_ai_model_with_functions

        response = request_function(messages, functions, "auto", GPT_4)

        # Determine if the model has called the function to end the dialogue.
        message = response["choices"][0]["message"]

        if (
            message.get("function_call")
            and message["function_call"]["name"] == "stop_dialogue"
        ):
            should_continue_dialogue = False

        elif (
            message.get("function_call")
            and message["function_call"]["name"] == "get_lines_of_dialogue"
        ):
            # Have received lines of dialogue from GPT-4.
            function_arguments = json.loads(message["function_call"]["arguments"])

            for line_of_dialogue in function_arguments.get("lines_of_dialogue"):
                messages.append({"role": "assistant", "content": line_of_dialogue})

            user_spoke_last = False
        elif message.get("role") == "assistant" and message.get("content") is not None:
            # the AI ignored our function to just return a single line of dialogue.
            messages.append(message)
            user_spoke_last = False
        else:
            # the message came from the user
            messages.append(message)
            user_spoke_last = True

    # print the messages
    for message in messages:
        output_colored_message("light_yellow", message["content"])


if __name__ == "__main__":
    main()
