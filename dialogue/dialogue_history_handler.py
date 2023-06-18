"""This module contains the definition of DialogueHistoryHandler, that handles the dialogue history of a conversation.
"""
from errors import InvalidParameterError


HOW_MANY_LINES_OF_DIALOGUE_TO_INCLUDE_IN_PROMPT = 20


class DialogueHistoryHandler:
    """Handles the dialogue history of a conversation."""

    def __init__(self):
        self._dialogue_history = []

    def get_dialogue_history(self) -> list[dict]:
        """Returns the dialogue history.

        Returns:
            list[dict]: the list of dicts that contain each line of dialogue.
        """
        return self._dialogue_history

    def add_dialogue_history_for_prompt(self, user_content):
        """Adds the last X lines of dialogue to the prompt that will be sent to an AI model.

        Args:
            user_content (str): part of the text that will be sent in the prompt to the AI model.

        Returns:
            str: part of the text that will be sent in the prompt to the AI model.
        """
        if len(self._dialogue_history) > 0:
            user_content += "\nLatest lines of dialogue:\n"
            user_content += "\n".join(
                [
                    line_of_dialogue["content"]
                    for line_of_dialogue in self._dialogue_history[
                        -HOW_MANY_LINES_OF_DIALOGUE_TO_INCLUDE_IN_PROMPT:
                    ]
                ]
            )

        return user_content

    def register_line_of_dialogue(self, line_of_dialogue: dict):
        """Registers a line of dialogue (in the message format of a GPT message) in the dialogue history.

        Args:
            line_of_dialogue (dict): the line of dialogue that will be registered in the dialogue history.

        Raises:
            InvalidParameterError: if 'line_of_dialogue' isn't a dictionary'.
            ValueError: if 'line_of_dialogue' isn't in the format of a message from GPT.
        """
        if not isinstance(line_of_dialogue, dict):
            raise InvalidParameterError(
                f"Attempted to register a line of dialogue, but 'line_of_dialogue' wasn't a dict: {line_of_dialogue}"
            )
        if not line_of_dialogue.get("role") or not line_of_dialogue.get("content"):
            raise ValueError(
                f"Attempted to register a line of dialogue, but the parameter passed wasn't in the expected format: {line_of_dialogue}"
            )

        self._dialogue_history.append(line_of_dialogue)
