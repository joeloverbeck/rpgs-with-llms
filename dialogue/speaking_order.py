from typing import List
from agents.agent import Agent
from defines.defines import GPT_3_5
from errors import CouldntDetermineNextSpeakerError, InvalidParameterError
from llms.messages import (
    get_message_from_gpt_response,
    load_arguments_of_message_with_function_call,
)


def is_agent_next_speaker(agent: Agent, next_speaker: Agent):
    return agent.get_name().lower() == next_speaker.get_name().lower()


def determine_agent_who_will_speak_now(
    next_speaker: Agent, involved_agents: List[Agent]
) -> Agent:
    if isinstance(next_speaker, str):
        raise InvalidParameterError(
            f"The function {determine_agent_who_will_speak_now.__name__} received a str 'next_speaker': {next_speaker}"
        )

    agent_who_will_speak_now = None

    for agent in involved_agents:
        if is_agent_next_speaker(agent, next_speaker):
            agent_who_will_speak_now = agent

    if agent_who_will_speak_now is None:
        error_message = f"Couldn't find the next speaker agent in the dialogue. Next speaker: {next_speaker}. Agents: {involved_agents}"
        raise CouldntDetermineNextSpeakerError(error_message)

    return agent_who_will_speak_now


def request_from_ai_model_who_will_speak_next(
    messages,
    functions,
    function_name,
    parameter_name,
    request_response_from_ai_model_with_functions_function,
):
    message = get_message_from_gpt_response(
        request_response_from_ai_model_with_functions_function(
            messages,
            functions,
            {"name": function_name},
            GPT_3_5,
        )
    )

    # Note: the message could have come from the user in case he's testing the prompts.

    if message.get("function_call"):
        function_arguments = load_arguments_of_message_with_function_call(message)

        return function_arguments.get(parameter_name)

    return message["content"].strip()
