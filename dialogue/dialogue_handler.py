"""This module contains the definition of the Dialogue Handler class, which handles the dialogue between two or more characters.
"""

import json
from defines.defines import GPT_4
from errors import InvalidParameterError
from input.confirmation import request_confirmation
from llms.api_requests import request_response_from_ai_model_with_functions
from llms.user_requests import request_response_from_user


class DialogueHandler:
    """Handles the dialogue between two or more characters, relying on an AI model."""

    def __init__(self, initial_messages):
        if not isinstance(initial_messages, list):
            raise InvalidParameterError(
                f"The class {DialogueHandler.__name__} expected 'initial_messages' to be a list, but it was: {initial_messages}"
            )

        self._messages = []

        system_content = "I am DialogueGPT. I have the responsibility of carrying on a dialogue between two or more characters until the context of "
        system_content += "the dialogue suggests that the dialogue should end."
        self._messages.append(
            {
                "role": "system",
                "content": system_content,
            }
        )

        self._messages.extend(initial_messages)

        self._functions = []
        self._functions.append(
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
        self._functions.append(
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

    def _get_message_function(self, user_spoke_last):
        if not user_spoke_last and request_confirmation(
            "Last 3 messages: \n"
            + "\n".join([msg["content"] for msg in self._messages[-3:]])
            + "\nDo you want to interject in the conversation?"
        ):
            return request_response_from_user

        return request_response_from_ai_model_with_functions

    def _handle_stop_dialogue(self, should_continue_dialogue, message):
        if (
            message.get("function_call")
            and message["function_call"]["name"] == "stop_dialogue"
        ):
            return False
        return should_continue_dialogue

    def _handle_lines_of_dialogue(self, user_spoke_last, message):
        if (
            message.get("function_call")
            and message["function_call"]["name"] == "get_lines_of_dialogue"
        ):
            function_arguments = json.loads(message["function_call"]["arguments"])

            for line_of_dialogue in function_arguments.get("lines_of_dialogue"):
                self._messages.append(
                    {"role": "assistant", "content": line_of_dialogue}
                )
            return False
        return user_spoke_last

    def _handle_assistant_message(self, user_spoke_last, message):
        if message.get("role") == "assistant" and message.get("content") is not None:
            self._messages.append(message)
            return False
        return user_spoke_last

    def perform_dialogue(self) -> list:
        """Performs a dialogue given the initial context passed during the initialization of this class.
        This dialogue will continue until the AI model stops the dialogue by using the function 'stop_dialogue',
        passed as an option through every request.

        Returns:
            list: the list of messages containing every line of dialogue.
        """
        # The variable 'user_spoke_last' will be used to determine if the user was the one who produced
        # the last line of dialogue; in that case, the code won't prompt him or her for another line.
        user_spoke_last = False

        should_continue_dialogue = True

        while should_continue_dialogue:
            # Only request confirmation if the user didn't speak last.
            if not user_spoke_last and request_confirmation(
                "Last 3 messages: \n"
                + "\n".join([msg["content"] for msg in self._messages[-3:]])
                + "\nDo you want to interject in the conversation?"
            ):
                request_function = request_response_from_user
            else:
                request_function = request_response_from_ai_model_with_functions

            response = request_function(self._messages, self._functions, "auto", GPT_4)

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
                    self._messages.append(
                        {"role": "assistant", "content": line_of_dialogue}
                    )

                user_spoke_last = False
            elif (
                message.get("role") == "assistant"
                and message.get("content") is not None
            ):
                # the AI ignored our function to just return a single line of dialogue.
                self._messages.append(message)
                user_spoke_last = False
            else:
                # the message came from the user
                self._messages.append(message)
                user_spoke_last = True

        return self._messages
