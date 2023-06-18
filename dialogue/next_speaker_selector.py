from datetime import datetime
from typing import Callable
from agents.agent import Agent
from dialogue.speaking_order import (
    determine_next_speaker,
    determine_who_is_going_to_speak_first,
)
from input.confirmation import request_confirmation


class NextSpeakerSelector:
    def __init__(
        self,
        current_timestamp: datetime,
        reason_for_conversation: str,
        player_agent: Agent | None,
        involved_agents: list[Agent],
        request_response_from_ai_model_with_functions_function: Callable[
            [list[dict], list[dict], str, str], dict
        ],
    ):
        self._next_speaker = None

        self._current_timestamp = current_timestamp
        self._reason_for_conversation = reason_for_conversation
        self._player_agent = player_agent
        self._involved_agents = involved_agents
        self._request_response_from_ai_model_with_functions_function = (
            request_response_from_ai_model_with_functions_function
        )

    def get_next_speaker(self) -> Agent:
        """Returns the agent who is set as the next speaker.

        Returns:
            Agent: the agent who is set as the next speaker.
        """
        return self._next_speaker

    def select_first_speaker(self):
        """Selects the agent who will speak first in a dialogue.

        Args:
            current_timestamp (datetime): the timestamp when the conversation is taking place.
            reason_for_conversation (str): why the conversation is taking place.
            player_agent (Agent | None): who is the player agent (if any; otherwise None)
            involved_agents (list[Agent]): a list with all the agents involved in the conversation.
            request_response_from_ai_model_with_functions_function (Callable[ [list[dict], list[dict], str, str], dict ]): the function that will receive a prompt
                and produce a response with the determination of who will speak first.
        """
        # Now we need to determine if the player will speak first, or if we will let
        # the AI model decide who speaks first.
        # The player can only have the option to speak first if 'player_agent' is not None.
        if self._player_agent is not None and request_confirmation(
            "Do you want to speak first?"
        ):
            self._next_speaker = self._player_agent.get_name()
        else:
            # When we kick off the dialogue, the AI model has to determine who is going to speak first.
            self._next_speaker = determine_who_is_going_to_speak_first(
                self._current_timestamp,
                self._reason_for_conversation,
                self._involved_agents,
                self._request_response_from_ai_model_with_functions_function,
            )

    def select_next_speaker(self):
        """This function ensures that the agent that will be chosen to speak next is not
        going to be the agent who spoke last. This is necessary because the AI model
        sometimes chooses the same agent to speak twice (or more) in a row, for obscure reasons.
        As a side effect, the internal attribute 'self._next_speaker' is set.
        """
        determined_next_speaker = determine_next_speaker(
            self._current_timestamp,
            self._reason_for_conversation,
            self._involved_agents,
            self._request_response_from_ai_model_with_functions_function,
        )

        # we would never want to have the same person talking twice in a row.
        if determined_next_speaker.lower() == self._next_speaker.lower():
            for agent in self._involved_agents:
                if agent.get_name().lower() != determined_next_speaker.lower():
                    determined_next_speaker = agent.get_name()
                    break

        self._next_speaker = determined_next_speaker
