"""This module contains the definition of SpeakerOtherThanPreviousSelector, which selects an agent
other than the one who spoke last.
"""
from random import choice, choices
from typing import List
from agents.agent import Agent


class SpeakerOtherThanPreviousSelector:
    """Class that selects an agent among the involved agents that isn't the one who spoke last."""

    def __init__(self, involved_agents: List[Agent]):
        if len(involved_agents) < 2:
            raise ValueError(
                f"The class {SpeakerOtherThanPreviousSelector.__name__} received 'involved_agents' with less than two agents: {involved_agents}"
            )

        self._involved_agents = involved_agents

        # Initialize the speaker counts
        self._speaker_counts = {agent: 0 for agent in involved_agents}

    def _choose_next_speaker_based_on_weighted_selection(
        self, eligible_speakers: List[Agent]
    ) -> Agent:
        """Chooses the next speaker based on a weighted selection.
        This is done because all the speakers are not equally likely to be chosen, given that we rely
        on an AI model to decide who speaks next (and that selection can at times be wonky.)

        Args:
            eligible_speakers (List[Agent]): the list of eligible speakers, that won't include the speaker who spoke last.
            total_count (int): the total count of how many times speakers have produced lines of dialogue.

        Returns:
            Agent: the chosen next speaker.
        """
        # Create a weighted selection - lower count means higher weight
        weights = [1 / (self._speaker_counts[agent] + 1) for agent in eligible_speakers]

        return choices(eligible_speakers, weights, k=1)[0]

    def select_next_speaker(self, determined_next_speaker: Agent) -> Agent:
        """Selects a speaker other than the speaker who spoke last.

        Args:
            determined_next_speaker (Agent): the agent who was determined to speak next.

        Returns:
            Agent: the agent selected to speak next.
        """
        # Filter out the last speaker
        eligible_speakers = [
            agent
            for agent in self._involved_agents
            if agent.get_name().lower() != determined_next_speaker.get_name().lower()
        ]

        # If all counts are zero, select randomly
        if all(self._speaker_counts[agent] == 0 for agent in eligible_speakers):
            selected_agent = choice(eligible_speakers)
        else:
            selected_agent = self._choose_next_speaker_based_on_weighted_selection(
                eligible_speakers
            )

        # Increment the count of the selected agent
        self._speaker_counts[selected_agent] += 1

        return selected_agent
