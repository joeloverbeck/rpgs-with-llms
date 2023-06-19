"""This module contains the definition of NextSpeakerRequester, which relies on an AI model to determine
the name of the character who will either speak first or speak next.
"""
from typing import Callable
from defines.defines import SYSTEM_ROLE, USER_ROLE
from dialogue.conversation_state import ConversationState
from dialogue.dialogue_history_handler import DialogueHistoryHandler
from dialogue.speaking_order import request_from_ai_model_who_will_speak_next
from dialogue.user_content import add_user_content_for_who_will_speak
from llms.functions import append_single_parameter_function
from llms.interface import AIModelInterface

WHO_WILL_SPEAK_FIRST_GPT_SYSTEM_CONTENT = "I am WhoWillSpeakFirstGPT. I have the responsibility of determining the exact name of the agent who will "
WHO_WILL_SPEAK_FIRST_GPT_SYSTEM_CONTENT += (
    "utter the first line of dialogue in a new conversation."
)
DETERMINE_WHO_WILL_SPEAK_FIRST_FUNCTION_NAME = "determine_who_will_speak_first"
DETERMINE_WHO_WILL_SPEAK_FIRST_FUNCTION_DESCRIPTION = "Determines the exact name of the character who will utter the first line of dialogue in this conversation."
CHARACTER_WHO_WILL_SPEAK_FIRST_PARAMETER_NAME = "character_who_will_speak_first"
CHARACTER_WHO_WILL_SPEAK_FIRST_PARAMETER_DESCRIPTION = "Exact name of the character who will utter the first line of dialogue in this conversation."


WHO_WILL_SPEAK_NEXT_GPT_SYSTEM_CONTENT = "I am WhoWillSpeakNextGPT. I have the responsibility of determining the exact name of the agent who will "
WHO_WILL_SPEAK_NEXT_GPT_SYSTEM_CONTENT += (
    "utter the next line of dialogue in a new conversation."
)
DETERMINE_WHO_WILL_SPEAK_NEXT_FUNCTION_NAME = "determine_who_will_speak_next"
DETERMINE_WHO_WILL_SPEAK_NEXT_FUNCTION_DESCRIPTION = "Determines the exact name of the character who will utter the next line of dialogue in this conversation."
CHARACTER_WHO_WILL_SPEAK_NEXT_PARAMETER_NAME = "character_who_will_speak_next"
CHARACTER_WHO_WILL_SPEAK_NEXT_PARAMETER_DESCRIPTION = "Exact name of the character who will utter the next line of dialogue in this conversation. "
CHARACTER_WHO_WILL_SPEAK_NEXT_PARAMETER_DESCRIPTION += (
    "Never choose the character who spoke last."
)


class NextSpeakerRequester:
    def __init__(
        self,
        conversation_state: ConversationState,
        dialogue_history_handler: DialogueHistoryHandler,
        ai_model_interface: AIModelInterface,
    ):
        self._conversation_state = conversation_state
        self._dialogue_history_handler = dialogue_history_handler
        self._ai_model_interface = ai_model_interface

    def _determine_speaker(
        self,
        system_content: str,
        user_content_conclusion: str,
        function_name: str,
        function_description: str,
        parameter_name: str,
        parameter_description: str,
    ):
        """Delegates asking the AI model for the name of the agent who will be the next speaker
        (either the first or the next).

        Args:
            system_content (str): what is the content message of the message with the role "system" to be sent to the AI.
            user_content_conclusion (str): what is the message that will conclude the content of the role "user" to be sent to the AI.
            function_name (str): the name of the function to be passed to the AI model so it will be called.
            function_description (str): the description of the function that the AI model will call.
            parameter_name (str): the name of the parameter that the AI model will fill.
            parameter_description (str): the description of the parameter that the AI model will fill.

        Returns:
            dict: the response from the AI model to the request.
        """
        messages = [{"role": SYSTEM_ROLE, "content": system_content}]

        user_content = add_user_content_for_who_will_speak(
            self._conversation_state,
            self._dialogue_history_handler,
        )

        user_content += user_content_conclusion
        messages.append({"role": USER_ROLE, "content": user_content})

        functions = []
        append_single_parameter_function(
            functions,
            function_name,
            function_description,
            parameter_name,
            "string",
            parameter_description,
        )

        return request_from_ai_model_who_will_speak_next(
            messages,
            functions,
            function_name,
            parameter_name,
            self._ai_model_interface,
        )

    def request_first_speaker(self) -> str:
        """Requests the name of the character who will speak first in the conversation.

        Returns:
            str: the name of the character who will utter the first line of dialogue.
        """
        return self._determine_speaker(
            WHO_WILL_SPEAK_FIRST_GPT_SYSTEM_CONTENT,
            "\nWhat is the name of the character who will utter the first line of dialogue?",
            DETERMINE_WHO_WILL_SPEAK_FIRST_FUNCTION_NAME,
            DETERMINE_WHO_WILL_SPEAK_FIRST_FUNCTION_DESCRIPTION,
            CHARACTER_WHO_WILL_SPEAK_FIRST_PARAMETER_NAME,
            CHARACTER_WHO_WILL_SPEAK_FIRST_PARAMETER_DESCRIPTION,
        )

    def request_next_speaker(self) -> str:
        """Requests the name of the character who will speak next in the conversation.

        Returns:
            str: the name of the character who will utter the next line of dialogue.
        """
        return self._determine_speaker(
            WHO_WILL_SPEAK_NEXT_GPT_SYSTEM_CONTENT,
            (
                "\nWhat is the name of the character who will utter the next line of dialogue?"
                " DON'T choose the name of the character who spoke the last line of dialogue."
            ),
            DETERMINE_WHO_WILL_SPEAK_NEXT_FUNCTION_NAME,
            DETERMINE_WHO_WILL_SPEAK_NEXT_FUNCTION_DESCRIPTION,
            CHARACTER_WHO_WILL_SPEAK_NEXT_PARAMETER_NAME,
            CHARACTER_WHO_WILL_SPEAK_NEXT_PARAMETER_DESCRIPTION,
        )
