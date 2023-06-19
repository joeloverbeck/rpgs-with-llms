from datetime import datetime
from agents.agent import Agent
from vector_databases.database_loader import DatabaseLoader
from vector_databases.database_querier import DatabaseQuerier

NUMBER_OF_RESULTS_FOR_RELATIONSHIP_WITH_INTERLOCUTOR_QUERY = 20


def add_relevant_memories_regarding_interlocutors(
    current_timestamp: datetime,
    user_content: str,
    agent_who_will_speak_now: Agent,
    involved_agents: list[Agent],
):
    index, memories_raw_data = DatabaseLoader(
        agent_who_will_speak_now.get_name()
    ).load()

    memories_database_querier = DatabaseQuerier(
        agent_who_will_speak_now.get_name(),
        current_timestamp,
        memories_raw_data,
        index,
    )

    for agent in involved_agents:
        if agent != agent_who_will_speak_now:
            relevant_memories = memories_database_querier.query(
                f"What is {agent_who_will_speak_now.get_name()}'s relationship with {agent.get_name()}?",
                NUMBER_OF_RESULTS_FOR_RELATIONSHIP_WITH_INTERLOCUTOR_QUERY,
            )

            user_content += f"Summary of relevant context from {agent_who_will_speak_now.get_name()}'s memory regarding {agent.get_name()}:\n"

            user_content += " ".join(relevant_memories)

            user_content += "\n"

    return user_content


def add_involved_agents_status(user_content: str, involved_agents: list[Agent]):
    for agent in involved_agents:
        user_content += f"{agent.get_name()}'s status: {agent.get_status()}\n"

    return user_content


def add_reason_for_conversation(user_content, reason_for_conversation):
    user_content += f"Reason for conversation: {reason_for_conversation}\n"

    return user_content


def add_characters_involved_in_conversation(user_content, involved_agents):
    user_content += (
        "Characters involved in conversation: "
        + ", ".join([agent.get_name() for agent in involved_agents])
        + "\n"
    )

    return user_content


def add_agent_statuses(user_content, involved_agents):
    for agent in involved_agents:
        user_content += f"{agent.get_name()}'s status: {agent.get_status()}\n"

    return user_content
