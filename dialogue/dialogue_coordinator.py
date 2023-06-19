"""This module contains the definition of the Dialogue Coordinator class, which handles the dialogue between two or more characters.
"""

from dialogue.contracts import ensure_dialogue_handler_initialization_contract
from dialogue.conversation_state import ConversationState
from dialogue.dialogue_continuation_handler import DialogueContinuationHandler
from dialogue.dialogue_history_handler import DialogueHistoryHandler
from dialogue.line_of_dialogue_producer import LineOfDialogueProducer
from dialogue.speaker_selector import SpeakerSelector
from llms.interface import AIModelInterface


class DialogueCoordinator:
    """Coordinates the dialogue between two or more characters, relying on an AI model."""

    def __init__(
        self,
        conversation_state: ConversationState,
        player_wants_to_speak_first: bool,
        ai_model_interface: AIModelInterface,
    ):
        """Initializates an instance of the DialogueCoordinator class.

        Args:
            conversation_state (ConversationState): the state of the conversation.
            player_wants_to_speak_first (bool): whether the player wants to speak first.
            request_response_from_ai_model_with_functions_function (Callable[ [list[dict], list[dict], str, str], dict ]): the function responsible
                for requesting responses from either the user or an AI model.
        """
        ensure_dialogue_handler_initialization_contract(
            conversation_state.get_involved_agents(),
            conversation_state.get_reason_for_conversation(),
        )

        self._ai_model_interface = ai_model_interface

        self._conversation_state = conversation_state

        self._dialogue_history_handler = DialogueHistoryHandler()
        self._speaker_selector = SpeakerSelector(
            self._conversation_state,
            self._dialogue_history_handler,
            self._ai_model_interface,
        )
        self._line_of_dialogue_producer = LineOfDialogueProducer(
            self._conversation_state,
            self._speaker_selector,
        )

        self._speaker_selector.select_first_speaker(player_wants_to_speak_first)

    def perform_dialogue(self) -> list[dict]:
        """Performs a dialogue given the initial context passed during the initialization of this class.
        This dialogue will continue until the AI model stops the dialogue by using the function 'stop_dialogue',
        passed as an option through every request.

        Returns:
            list[dict]: the list of messages containing every line of dialogue.
        """
        dialogue_continuation_handler = DialogueContinuationHandler(
            self._conversation_state,
            self._dialogue_history_handler,
            self._ai_model_interface,
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
                self._speaker_selector.select_next_speaker()

        return self._dialogue_history_handler.get_dialogue_history()
