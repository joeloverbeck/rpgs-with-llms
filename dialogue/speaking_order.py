from datetime import datetime
from agents.agent import Agent
from defines.defines import GPT_3_5, SYSTEM_ROLE, USER_ROLE
from dialogue.user_content import add_user_content_for_who_will_speak
from errors import CouldntDetermineNextSpeakerError
from llms.functions import append_single_parameter_function
from llms.messages import (
    get_message_from_gpt_response,
    load_arguments_of_message_with_function_call,
)

WHO_WILL_SPEAK_FIRST_GPT_SYSTEM_CONTENT = "I am WhoWillSpeakFirstGPT. I have the responsibility of determining the exact name of the agent who will "
WHO_WILL_SPEAK_FIRST_GPT_SYSTEM_CONTENT += (
    "utter the first line of dialogue in a new conversation."
)
DETERMINE_WHO_WILL_SPEAK_FIRST_FUNCTION_NAME = "determine_who_will_speak_first"
DETERMINE_WHO_WILL_SPEAK_FIRST_FUNCTION_DESCRIPTION = "Determines the exact name of the character who will utter the first line of dialogue in this conversation."
CHARACTER_WHO_WILL_SPEAK_FIRST_PARAMETER_NAME = "character_who_will_speak_first"
CHARACTER_WHO_WILL_SPEAK_FIRST_PARAMETER_DESCRIPTION = "Exact name of the character who will utter the first line of dialogue in this conversation."


WHO_WILL_SPEAK_NEXT_GPT_SYSTEM_CONTENT = "I am WhoWillSpeakNextGPT. I have the responsibility of determining the exact name of the agent who will "
WHO_WILL_SPEAK_NEXT_GPT_SYSTEM_CONTENT += (
    "utter the next line of dialogue in a new conversation."
)
DETERMINE_WHO_WILL_SPEAK_NEXT_FUNCTION_NAME = "determine_who_will_speak_next"
DETERMINE_WHO_WILL_SPEAK_NEXT_FUNCTION_DESCRIPTION = "Determines the exact name of the character who will utter the next line of dialogue in this conversation."
CHARACTER_WHO_WILL_SPEAK_NEXT_PARAMETER_NAME = "character_who_will_speak_next"
CHARACTER_WHO_WILL_SPEAK_NEXT_PARAMETER_DESCRIPTION = "Exact name of the character who will utter the next line of dialogue in this conversation. "
CHARACTER_WHO_WILL_SPEAK_NEXT_PARAMETER_DESCRIPTION += (
    "Never choose the character who spoke last."
)


def is_agent_next_speaker(agent, next_speaker):
    return agent.get_name().lower() == next_speaker.lower()


def determine_agent_who_will_speak_now(next_speaker, involved_agents):
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


def determine_next_speaker(
    current_timestamp: datetime,
    reason_for_conversation: str,
    involved_agents: list[Agent],
    request_response_from_ai_model_with_functions_function,
) -> str:
    """Determines the name of the character who will speak the next line of dialogue.

    Returns:
        str: the exact name of the character who will speak the next line of dialogue.
    """
    messages = []

    messages.append(
        {
            "role": SYSTEM_ROLE,
            "content": WHO_WILL_SPEAK_NEXT_GPT_SYSTEM_CONTENT,
        }
    )

    user_content = add_user_content_for_who_will_speak(
        current_timestamp,
        reason_for_conversation,
        involved_agents,
    )

    user_content += "\nWhat is the name of the name of the character who will utter the next line of dialogue?"
    user_content += " Choose a character other than the character who spoke the last line of dialogue."

    messages.append({"role": USER_ROLE, "content": user_content})

    functions = []
    append_single_parameter_function(
        functions,
        DETERMINE_WHO_WILL_SPEAK_NEXT_FUNCTION_NAME,
        DETERMINE_WHO_WILL_SPEAK_NEXT_FUNCTION_DESCRIPTION,
        CHARACTER_WHO_WILL_SPEAK_NEXT_PARAMETER_NAME,
        "string",
        CHARACTER_WHO_WILL_SPEAK_NEXT_PARAMETER_DESCRIPTION,
    )

    return request_from_ai_model_who_will_speak_next(
        messages,
        functions,
        DETERMINE_WHO_WILL_SPEAK_NEXT_FUNCTION_NAME,
        CHARACTER_WHO_WILL_SPEAK_NEXT_PARAMETER_NAME,
        request_response_from_ai_model_with_functions_function,
    )


def determine_who_is_going_to_speak_first(
    current_timestamp: datetime,
    reason_for_conversation: str,
    involved_agents: list[Agent],
    request_response_from_ai_model_with_functions_function,
):
    messages = []

    messages.append(
        {
            "role": SYSTEM_ROLE,
            "content": WHO_WILL_SPEAK_FIRST_GPT_SYSTEM_CONTENT,
        }
    )

    user_content = add_user_content_for_who_will_speak(
        current_timestamp,
        reason_for_conversation,
        involved_agents,
    )

    user_content += "\nWhat is the name of the name of the character who will utter the first line of dialogue?"

    messages.append({"role": USER_ROLE, "content": user_content})

    functions = []
    append_single_parameter_function(
        functions,
        DETERMINE_WHO_WILL_SPEAK_FIRST_FUNCTION_NAME,
        DETERMINE_WHO_WILL_SPEAK_FIRST_FUNCTION_DESCRIPTION,
        CHARACTER_WHO_WILL_SPEAK_FIRST_PARAMETER_NAME,
        "string",
        CHARACTER_WHO_WILL_SPEAK_FIRST_PARAMETER_DESCRIPTION,
    )

    return request_from_ai_model_who_will_speak_next(
        messages,
        functions,
        DETERMINE_WHO_WILL_SPEAK_FIRST_FUNCTION_NAME,
        CHARACTER_WHO_WILL_SPEAK_FIRST_PARAMETER_NAME,
        request_response_from_ai_model_with_functions_function,
    )
