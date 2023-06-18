"""This module defines the class NextSpeakerSelector, that handles selecting the first speaker in a conversation,
as well as the next speaker.
"""
from datetime import datetime
from typing import Callable
from typing import List
from agents.agent import Agent
from dialogue.dialogue_history_handler import DialogueHistoryHandler
from dialogue.next_speaker_requester import NextSpeakerRequester
from dialogue.speaker_other_than_previous_selector import (
    SpeakerOtherThanPreviousSelector,
)
from errors import CouldntFindMatchingAgentError


class NextSpeakerSelector:
    """This class handles selecting who is going to speak first in a dialogue, as well as who is going to speak next."""

    def __init__(
        self,
        current_timestamp: datetime,
        reason_for_conversation: str,
        player_agent: Agent | None,
        involved_agents: List[Agent],
        dialogue_history_handler: DialogueHistoryHandler,
        request_ai_response_with_functions_function: Callable[
            [List[dict], List[dict], str, str], dict
        ],
    ):
        """Creates an instance of the class NextSpeakerSelector

        Args:
            current_timestamp (datetime): the timestamp when this simulation takes place.
            reason_for_conversation (str): the reason for the conversation
            player_agent (Agent | None): whether or not there is a player agent involved
            involved_agents (List[Agent]): the list of involved agents in the conversation
            request_ai_response_with_functions_function (Callable[ [List[dict], List[dict], str, str], dict ]): the function that generates
                responses to requests, either by sending them to the user or to an AI model

        Raises:
            ValueError: if received 'involved_agents' with less than two agents
        """
        if len(involved_agents) < 2:
            raise ValueError(
                f"Initialized {NextSpeakerSelector.__name__} with less than two involved agents: {involved_agents}"
            )

        # Initialize the speaker to the first of the 'involved_agents' list, just in case.
        self._next_speaker = involved_agents[0]

        self._current_timestamp = current_timestamp
        self._reason_for_conversation = reason_for_conversation
        self._player_agent = player_agent
        self._involved_agents = involved_agents
        self._dialogue_history_handler = dialogue_history_handler
        self._request_ai_response_with_functions_function = (
            request_ai_response_with_functions_function
        )

        self._speaker_other_than_previous_selector = SpeakerOtherThanPreviousSelector(
            self._involved_agents
        )

        self._next_speaker_requester = NextSpeakerRequester(
            self._current_timestamp,
            self._reason_for_conversation,
            self._involved_agents,
            self._dialogue_history_handler,
            self._request_ai_response_with_functions_function,
        )

    def _set_next_speaker(self, next_speaker: Agent):
        if not isinstance(next_speaker, Agent):
            raise TypeError(
                f"Attempted to set a next speaker that wasn't an agent: {next_speaker}"
            )

        self._next_speaker = next_speaker

    def _find_involved_agent_with_matching_name(self, name):
        matching_agent = next(
            (
                agent
                for agent in self._involved_agents
                if agent.get_name().lower() == name.lower()
            ),
            None,
        )

        if matching_agent is None:
            raise CouldntFindMatchingAgentError(
                f"The function {self._find_involved_agent_with_matching_name.__name__} failed to find involved agent with name '{name}'"
            )

        return matching_agent

    def get_next_speaker(self) -> Agent:
        """Returns the agent who is set as the next speaker.

        Returns:
            Agent: the agent who is set as the next speaker.
        """
        return self._next_speaker

    def select_first_speaker(self, player_wants_to_speak_first: bool):
        """Selects the agent who will speak first in a dialogue.

        Args:
            player_wants_to_speak_first (bool): whether the player wants to speak first
        """
        # We need to determine if the player will speak first, or if we will let
        # the AI model decide who speaks first.
        # The player can only have the option to speak first if 'player_agent' is not None.
        if player_wants_to_speak_first and self._player_agent is not None:
            self._set_next_speaker(self._player_agent)
        else:
            # When we kick off the dialogue, the AI model has to determine who is going to speak first.
            self._set_next_speaker(
                self._find_involved_agent_with_matching_name(
                    self._next_speaker_requester.request_first_speaker()
                )
            )

    def select_next_speaker(self):
        """This function ensures that the agent that will be chosen to speak next is not
        going to be the agent who spoke last. This is necessary because the AI model
        sometimes chooses the same agent to speak twice (or more) in a row, for obscure reasons.
        As a side effect, the internal attribute 'self._next_speaker' is set.
        """
        matching_agent = self._find_involved_agent_with_matching_name(
            self._next_speaker_requester.request_next_speaker()
        )

        # we would never want to have the same person talking twice in a row.
        if matching_agent.get_name().lower() == self._next_speaker.get_name().lower():
            self._set_next_speaker(
                self._speaker_other_than_previous_selector.select_next_speaker(
                    matching_agent
                )
            )
        else:
            # Must locate the agent with the matching name to 'determined_next_speaker'
            self._set_next_speaker(matching_agent)
