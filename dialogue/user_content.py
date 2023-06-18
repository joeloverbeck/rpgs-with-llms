from datetime import datetime
from typing import List
from agents.agent import Agent
from datetime_utils import format_timestamp_for_prompt
from dialogue.dialogue_history_handler import DialogueHistoryHandler
from dialogue.prompting import (
    add_agent_statuses,
    add_characters_involved_in_conversation,
    add_reason_for_conversation,
)


def add_user_content_for_who_will_speak(
    current_timestamp: datetime,
    reason_for_conversation: str,
    involved_agents: List[Agent],
    dialogue_history_handler: DialogueHistoryHandler,
):
    user_content = f"{format_timestamp_for_prompt(current_timestamp)}\n"

    user_content = add_characters_involved_in_conversation(
        user_content, involved_agents
    )

    user_content = add_agent_statuses(user_content, involved_agents)

    user_content = add_reason_for_conversation(user_content, reason_for_conversation)

    user_content = dialogue_history_handler.add_dialogue_history_for_prompt(
        user_content
    )

    return user_content
