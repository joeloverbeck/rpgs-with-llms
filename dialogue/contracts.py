from errors import (
    AgentCharacterSummaryMissingError,
    AgentStatusMissingError,
    InvalidParameterError,
)


def ensure_dialogue_handler_initialization_contract(involved_agents, reason_for_conversation):
    if involved_agents is None:
        raise InvalidParameterError(
            "The DialogueHandler expected 'involved_agents' not to be None"
        )
    if len(involved_agents) < 2:
        raise ValueError(
            f"The DialogueHandler was asked to hold a conversation with less than two people: {involved_agents}"
        )
    if reason_for_conversation is None:
        raise InvalidParameterError(
            "The DialogueHandler expected 'reason_for_conversation' not to be None."
        )

    for agent in involved_agents:
        if agent.get_status() is None:
            raise AgentStatusMissingError(
                f"Attempted to involve '{agent.get_name()}' in a dialogue, but the status wasn't set."
            )
        if agent.get_character_summary() is None:
            raise AgentCharacterSummaryMissingError(
                f"Attempted to involve '{agent.get_name()}' in a dialogue, but the character summary wasn't set."
            )
