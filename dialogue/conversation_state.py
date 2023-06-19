from datetime import datetime
from typing import List

from agents.agent import Agent


class ConversationState:
    def __init__(
        self,
        current_timestamp: datetime,
        reason_for_conversation: str,
        player_agent: Agent | None,
        involved_agents: List[Agent],
    ):
        if len(involved_agents) < 2:
            raise ValueError(
                f"Initialized {ConversationState.__name__} with less than two involved agents: {involved_agents}"
            )

        self._current_timestamp = current_timestamp
        self._reason_for_conversation = reason_for_conversation
        self._player_agent = player_agent
        self._involved_agents = involved_agents

    def get_current_timestamp(self) -> datetime:
        return self._current_timestamp

    def get_reason_for_conversation(self) -> str:
        return self._reason_for_conversation

    def get_player_agent(self) -> Agent | None:
        return self._player_agent

    def get_involved_agents(self) -> List[Agent]:
        return self._involved_agents
