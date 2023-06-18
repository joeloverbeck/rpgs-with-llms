from typing import Callable
from datetime import datetime
from agents.agent import Agent
from datetime_utils import format_timestamp_for_prompt
from defines.defines import GPT_3_5, SYSTEM_ROLE, USER_ROLE
from dialogue.dialogue_history_handler import DialogueHistoryHandler
from dialogue.prompting import add_involved_agents_status, add_reason_for_conversation
from llms.functions import append_single_parameter_function
from llms.messages import (
    get_message_from_gpt_response,
    load_arguments_of_message_with_function_call,
)

SHOULD_STOP_DIALOGUE_GPT_SYSTEM_CONTENT = "I am ShouldStopDialogueDeterminerGPT. I have the responsibility of determining if the ongoing dialogue should realistically "
SHOULD_STOP_DIALOGUE_GPT_SYSTEM_CONTENT += (
    "end now, given the context of the conversation and the latest lines of dialogue."
)
SHOULD_STOP_DIALOGUE_FUNCTION_NAME = "should_stop_dialogue"
SHOULD_STOP_DIALOGUE_FUNCTION_DESCRIPTION = "Determines if the dialogue has reached a natural conclusion, given the context of the conversation and "
SHOULD_STOP_DIALOGUE_FUNCTION_DESCRIPTION += "the latest lines of dialogue."
SHOULD_STOP_DIALOGUE_PARAMETER_NAME = "should_stop_dialogue"
SHOULD_STOP_DIALOGUE_PARAMETER_DESCRIPTION = "Whether or not the dialogue has reached a natural conclusion, given the context of the conversation and "
SHOULD_STOP_DIALOGUE_PARAMETER_DESCRIPTION += "the latest lines of dialogue."


class DialogueContinuationHandler:
    def __init__(
        self,
        current_timestamp: datetime,
        reason_for_conversation: str,
        involved_agents: list[Agent],
        dialogue_history_handler: DialogueHistoryHandler,
        request_response_from_ai_model_with_functions_function: Callable[
            [list[dict], list[dict], str, str], dict
        ],
    ):
        self._should_dialogue_continue = True

        self._current_timestamp = current_timestamp
        self._reason_for_conversation = reason_for_conversation
        self._involved_agents = involved_agents
        self._dialogue_history_handler = dialogue_history_handler
        self._request_response_from_ai_model_with_functions_function = (
            request_response_from_ai_model_with_functions_function
        )

    def should_dialogue_continue(self) -> bool:
        return self._should_dialogue_continue

    def _determine_user_content_to_determine_if_dialogue_should_end(self) -> str:
        """Determines what should be added to the prompt that will be sent to the AI model
        so that it determines whether or not the dialogue should end.

        Returns:
            str: the user content that will be sent in the prompt to the AI model.
        """
        user_content = ""

        user_content += f"{format_timestamp_for_prompt(self._current_timestamp)}\n"

        user_content = add_involved_agents_status(user_content, self._involved_agents)

        user_content = add_reason_for_conversation(
            user_content, self._reason_for_conversation
        )

        user_content = self._dialogue_history_handler.add_dialogue_history_for_prompt(
            user_content
        )

        user_content += "\nGiven the context and the latest lines of dialogue, should the dialogue end now "
        user_content += "because it has reached a natural conclusion?"

        return user_content

    def determine_if_dialogue_should_end(self):
        """Given the current state of the dialogue, this function delegates to the AI model
        the decision of whether or not the dialogue should end now.
        """
        messages = []

        messages.append(
            {
                "role": SYSTEM_ROLE,
                "content": SHOULD_STOP_DIALOGUE_GPT_SYSTEM_CONTENT,
            }
        )

        messages.append(
            {
                "role": USER_ROLE,
                "content": self._determine_user_content_to_determine_if_dialogue_should_end(),
            }
        )

        functions = []
        append_single_parameter_function(
            functions,
            SHOULD_STOP_DIALOGUE_FUNCTION_NAME,
            SHOULD_STOP_DIALOGUE_FUNCTION_DESCRIPTION,
            SHOULD_STOP_DIALOGUE_PARAMETER_NAME,
            "boolean",
            SHOULD_STOP_DIALOGUE_PARAMETER_DESCRIPTION,
        )

        message = get_message_from_gpt_response(
            self._request_response_from_ai_model_with_functions_function(
                messages,
                functions,
                {"name": SHOULD_STOP_DIALOGUE_FUNCTION_NAME},
                GPT_3_5,
            )
        )

        # Note: the message could have come from the user, for example in the case
        # that the user is testing prompts.

        if message.get("function_call"):
            function_arguments = load_arguments_of_message_with_function_call(message)

            should_dialogue_stop = function_arguments.get(
                SHOULD_STOP_DIALOGUE_PARAMETER_NAME
            )
        else:
            should_dialogue_stop = bool(message["content"].lower().strip() == "true")

        if should_dialogue_stop:
            self._should_dialogue_continue = False
