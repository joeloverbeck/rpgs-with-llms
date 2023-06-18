"""This module contains the definition of the Dialogue Handler class, which handles the dialogue between two or more characters.
"""

from datetime import datetime
from typing import Callable
from agents.agent import Agent
from dialogue.contracts import ensure_dialogue_handler_initialization_contract
from dialogue.dialogue_continuation_handler import DialogueContinuationHandler
from dialogue.dialogue_history_handler import DialogueHistoryHandler
from dialogue.line_of_dialogue_producer import LineOfDialogueProducer
from dialogue.next_speaker_selector import NextSpeakerSelector


class DialogueCoordinator:
    """Handles the dialogue between two or more characters, relying on an AI model."""

    def __init__(
        self,
        involved_agents: list[Agent],
        player_agent: Agent | None,
        reason_for_conversation: str,
        current_timestamp: datetime,
        request_response_from_ai_model_with_functions_function: Callable[
            [list[dict], list[dict], str, str], dict
        ],
    ):
        ensure_dialogue_handler_initialization_contract(
            involved_agents, reason_for_conversation
        )

        self._current_timestamp = current_timestamp

        self._request_response_from_ai_model_with_functions_function = (
            request_response_from_ai_model_with_functions_function
        )

        self._reason_for_conversation = reason_for_conversation
        self._involved_agents = involved_agents
        self._player_agent = player_agent

        self._dialogue_history_handler = DialogueHistoryHandler()
        self._next_speaker_selector = NextSpeakerSelector(
            self._current_timestamp,
            self._reason_for_conversation,
            self._player_agent,
            self._involved_agents,
            self._request_response_from_ai_model_with_functions_function,
        )
        self._line_of_dialogue_producer = LineOfDialogueProducer(
            self._current_timestamp,
            self._reason_for_conversation,
            self._player_agent,
            self._involved_agents,
            self._next_speaker_selector,
        )

        self._next_speaker_selector.select_first_speaker()

    def perform_dialogue(self) -> list[dict]:
        """Performs a dialogue given the initial context passed during the initialization of this class.
        This dialogue will continue until the AI model stops the dialogue by using the function 'stop_dialogue',
        passed as an option through every request.

        Returns:
            list[dict]: the list of messages containing every line of dialogue.
        """
        dialogue_continuation_handler = DialogueContinuationHandler(
            self._reason_for_conversation,
            self._involved_agents,
            self._dialogue_history_handler,
            self._request_response_from_ai_model_with_functions_function,
        )

        while dialogue_continuation_handler.should_dialogue_continue():
            # Delegate producing a line of dialogue, and then story it in the dialogue history.
            self._dialogue_history_handler.register_line_of_dialogue(
                self._line_of_dialogue_producer.produce_line_of_dialogue(
                    self._dialogue_history_handler
                )
            )

            dialogue_continuation_handler.determine_if_dialogue_should_end()

            if dialogue_continuation_handler.should_dialogue_continue():
                self._next_speaker_selector.select_next_speaker()

        return self._dialogue_history_handler.get_dialogue_history()
