"""This module contains the definition of the Dialogue Handler class, which handles the dialogue between two or more characters.
"""

import json
from defines.defines import (
    ASSISTANT_ROLE,
    DIALOGUE_GPT_SYSTEM_CONTENT,
    GPT_4,
    HOW_MANY_LINES_OF_DIALOGUE_TO_SHOW_TO_USER,
    LINES_OF_DIALOGUE_PARAMETER_DESCRIPTION,
    LINES_OF_DIALOGUE_PARAMETER_NAME,
    STOP_DIALOGUE_FUNCTION_DESCRIPTION,
    STOP_DIALOGUE_FUNCTION_NAME,
    SYSTEM_ROLE,
    WRITE_LINES_OF_DIALOGUE_FUNCTION_DESCRIPTION,
    WRITE_LINES_OF_DIALOGUE_FUNCTION_NAME,
)
from errors import InvalidParameterError
from input.confirmation import request_confirmation
from llms.messages import get_message_from_gpt_response
from llms.user_requests import request_response_from_user


class DialogueHandler:
    """Handles the dialogue between two or more characters, relying on an AI model."""

    def __init__(
        self, initial_messages, request_response_from_ai_model_with_functions_function
    ):
        if not isinstance(initial_messages, list):
            raise InvalidParameterError(
                f"The class {DialogueHandler.__name__} expected 'initial_messages' to be a list, but it was: {initial_messages}"
            )

        self._request_reponse_from_ai_model_with_functions_function = (
            request_response_from_ai_model_with_functions_function
        )

        self._messages = []

        self._messages.append(
            {
                "role": SYSTEM_ROLE,
                "content": DIALOGUE_GPT_SYSTEM_CONTENT,
            }
        )

        self._messages.extend(initial_messages)

        self._functions = []
        self._functions.append(
            {
                "name": STOP_DIALOGUE_FUNCTION_NAME,
                "description": STOP_DIALOGUE_FUNCTION_DESCRIPTION,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            }
        )
        self._functions.append(
            {
                "name": WRITE_LINES_OF_DIALOGUE_FUNCTION_NAME,
                "description": WRITE_LINES_OF_DIALOGUE_FUNCTION_DESCRIPTION,
                "parameters": {
                    "type": "object",
                    "properties": {
                        LINES_OF_DIALOGUE_PARAMETER_NAME: {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": LINES_OF_DIALOGUE_PARAMETER_DESCRIPTION,
                            },
                        }
                    },
                    "required": [LINES_OF_DIALOGUE_PARAMETER_NAME],
                },
            }
        )

    def _crash_if_content_in_last_x_messages_was_invalid(self, last_x_messages):
        for msg in last_x_messages:
            if msg["content"] is None:
                raise ValueError(
                    f"Invalid message content in last {HOW_MANY_LINES_OF_DIALOGUE_TO_SHOW_TO_USER} messages: {last_x_messages}"
                )

    def _determine_request_response_function(self, user_spoke_last, last_x_messages):
        # Only request confirmation if the user didn't speak last.
        if not user_spoke_last and request_confirmation(
            "Last 3 messages: \n"
            + "\n".join([msg["content"] for msg in last_x_messages])
            + "\nDo you want to interject in the conversation?"
        ):
            request_function = request_response_from_user
        else:
            request_function = (
                self._request_reponse_from_ai_model_with_functions_function
            )

        return request_function

    def _store_lines_of_dialogue_produced_by_gpt(self, message: dict):
        function_arguments = json.loads(message["function_call"]["arguments"])

        for line_of_dialogue in function_arguments.get(
            LINES_OF_DIALOGUE_PARAMETER_NAME
        ):
            self._messages.append({"role": ASSISTANT_ROLE, "content": line_of_dialogue})

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
            last_x_messages = self._messages[
                -HOW_MANY_LINES_OF_DIALOGUE_TO_SHOW_TO_USER:
            ]

            self._crash_if_content_in_last_x_messages_was_invalid(last_x_messages)

            request_function = self._determine_request_response_function(
                user_spoke_last, last_x_messages
            )

            # In the following call, the 'auto' parameter means that the AI model will choose among the functions available, if necessary.
            # That parameter is required for the OpenAI GPT API.
            response = request_function(self._messages, self._functions, "auto", GPT_4)

            # Determine if the model has called the function to end the dialogue.
            message = get_message_from_gpt_response(response)

            if (
                message.get("function_call")
                and message["function_call"]["name"] == STOP_DIALOGUE_FUNCTION_NAME
            ):
                should_continue_dialogue = False

            if (
                message.get("function_call")
                and message["function_call"]["name"]
                == WRITE_LINES_OF_DIALOGUE_FUNCTION_NAME
            ):
                # Have received lines of dialogue from GPT-4.
                self._store_lines_of_dialogue_produced_by_gpt(message)

                user_spoke_last = False

            if (
                message.get("role") == ASSISTANT_ROLE
                and message.get("content") is not None
            ):
                # the AI ignored our function to just return a single line of dialogue.
                self._messages.append(message)

                user_spoke_last = False

            if message.get("content") != self._messages[-1:][0].get("content"):
                # the message came from the user
                self._messages.append(message)

                user_spoke_last = True

        return self._messages
