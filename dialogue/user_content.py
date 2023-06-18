from datetime_utils import format_timestamp_for_prompt
from dialogue.prompting import (
    add_agent_statuses,
    add_characters_involved_in_conversation,
    add_reason_for_conversation,
)


def add_user_content_for_who_will_speak(
    current_timestamp, reason_for_conversation, involved_agents
):
    user_content = f"{format_timestamp_for_prompt(current_timestamp)}\n"

    user_content = add_characters_involved_in_conversation(
        user_content, involved_agents
    )

    user_content = add_agent_statuses(user_content, involved_agents)

    user_content = add_reason_for_conversation(user_content, reason_for_conversation)

    return user_content
