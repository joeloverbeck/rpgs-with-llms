"""This module contains the definition of the Dialogue Handler class, which handles the dialogue between two or more characters.
"""

from datetime import datetime
from agents.agent import Agent
from datetime_utils import format_timestamp_for_prompt
from defines.defines import (
    ASSISTANT_ROLE,
    GPT_3_5,
    GPT_4,
    SYSTEM_ROLE,
    USER_ROLE,
)
from errors import (
    AgentStatusMissingError,
    CouldntDetermineNextSpeakerError,
    InvalidParameterError,
)
from input.confirmation import request_confirmation
from llms.functions import append_single_parameter_function
from llms.messages import (
    get_message_from_gpt_response,
    load_arguments_of_message_with_function_call,
)
from memories.memories_database_loader import MemoriesDatabaseLoader
from memories.memories_database_querier import MemoriesDatabaseQuerier

STOP_DIALOGUE_FUNCTION_NAME = "stop_dialogue"
STOP_DIALOGUE_FUNCTION_DESCRIPTION = "Stops the dialogue if the latest utterances make it appropriate for the dialogue to end now."


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

PRODUCE_LINE_OF_DIALOGUE_GPT_SYSTEM_CONTENT = "I am LineOfDialogueProducerGPT. I have the responsibility of writing the following line "
PRODUCE_LINE_OF_DIALOGUE_GPT_SYSTEM_CONTENT += "of dialogue in this conversation."
WRITE_LINE_OF_DIALOGUE_FUNCTION_NAME = "write_line_of_dialogue"
WRITE_LINE_OF_DIALOGUE_FUNCTION_DESCRIPTION = "write_line_of_dialogue"
LINE_OF_DIALOGUE_PARAMETER_NAME = "line_of_dialogue"
LINE_OF_DIALOGUE_PARAMETER_DESCRIPTION = (
    "The line of dialogue that the character will utter."
)
LINE_OF_DIALOGUE_PARAMETER_DESCRIPTION += "The format is the following: name of the character, followed by a colon, followed by the line of dialogue, "
LINE_OF_DIALOGUE_PARAMETER_DESCRIPTION += "that can be arbitrarily long. Snippets of narration can be included in parentheses."

SHOULD_STOP_DIALOGUE_GPT_SYSTEM_CONTENT = "I am ShouldStopDialogueDeterminerGPT. I have the responsibility of determining if the ongoing dialogue should realistically "
SHOULD_STOP_DIALOGUE_GPT_SYSTEM_CONTENT += (
    "end now, given the context of the conversation and the last lines of dialogue."
)
SHOULD_STOP_DIALOGUE_FUNCTION_NAME = "should_stop_dialogue"
SHOULD_STOP_DIALOGUE_FUNCTION_DESCRIPTION = "Determines if the dialogue should stop now, given the context of the conversation and the last lines of dialogue."
SHOULD_STOP_DIALOGUE_PARAMETER_NAME = "should_stop_dialogue"
SHOULD_STOP_DIALOGUE_PARAMETER_DESCRIPTION = "Whether or not the dialogue should stop now, given the context of the conversation and the last lines of dialogue."

HOW_MANY_LINES_OF_DIALOGUE_TO_SHOW_TO_USER = 4


class DialogueHandler:
    """Handles the dialogue between two or more characters, relying on an AI model."""

    def __init__(
        self,
        involved_agents: list[Agent],
        player_agent: Agent | None,
        reason_for_conversation: str,
        current_timestamp: datetime,
        request_response_from_ai_model_with_functions_function,
    ):
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

        self._current_timestamp = current_timestamp

        self._request_response_from_ai_model_with_functions_function = (
            request_response_from_ai_model_with_functions_function
        )

        self._reason_for_conversation = reason_for_conversation
        self._involved_agents = involved_agents
        self._player_agent = player_agent

        self._dialogue_history = []

        if self._player_agent is not None and request_confirmation(
            "Do you want to speak first?"
        ):
            self._next_speaker = self._player_agent.get_name()
        else:
            # When we kick off the dialogue, the AI model has to determine who is going to speak first.
            self._next_speaker = self._determine_who_is_going_to_speak_first()

    def _is_agent_next_speaker(self, agent):
        return agent.get_name().lower() == self._next_speaker.lower()

    def _determine_if_dialogue_should_end(self):
        messages = []

        messages.append(
            {
                "role": SYSTEM_ROLE,
                "content": SHOULD_STOP_DIALOGUE_GPT_SYSTEM_CONTENT,
            }
        )

        user_content = ""

        user_content = self._add_involved_agents_status(user_content)

        user_content = self._add_reason_for_conversation(user_content)

        user_content = self._add_dialogue_history(user_content)

        user_content += "\nGiven the context and the last lines of dialogue, should the dialogue end now?"

        messages.append({"role": USER_ROLE, "content": user_content})

        functions = []
        append_single_parameter_function(
            functions,
            SHOULD_STOP_DIALOGUE_FUNCTION_NAME,
            SHOULD_STOP_DIALOGUE_FUNCTION_DESCRIPTION,
            SHOULD_STOP_DIALOGUE_PARAMETER_NAME,
            "boolean",
            SHOULD_STOP_DIALOGUE_PARAMETER_DESCRIPTION,
        )

        response = self._request_response_from_ai_model_with_functions_function(
            messages,
            functions,
            {"name": SHOULD_STOP_DIALOGUE_FUNCTION_NAME},
            GPT_3_5,
        )

        function_arguments = load_arguments_of_message_with_function_call(
            get_message_from_gpt_response(response)
        )

        return function_arguments.get(SHOULD_STOP_DIALOGUE_PARAMETER_NAME)

    def _add_involved_agents_status(self, user_content):
        for agent in self._involved_agents:
            user_content += f"{agent.get_name()}'s status: {agent.get_status()}\n"

        return user_content

    def _add_reason_for_conversation(self, user_content):
        user_content += f"\nReason for conversation: {self._reason_for_conversation}"

        return user_content

    def _add_dialogue_history(self, user_content):
        if len(self._dialogue_history) > 0:
            user_content += "\nLatest lines of dialogue:\n"
            user_content += "\n".join(
                [
                    line_of_dialogue["content"]
                    for line_of_dialogue in self._dialogue_history[-10:]
                ]
            )

        return user_content

    def _determine_agent_who_will_speak_now(self):
        agent_who_will_speak_now = None

        for agent in self._involved_agents:
            if self._is_agent_next_speaker(agent):
                agent_who_will_speak_now = agent

        if agent_who_will_speak_now is None:
            error_message = f"Couldn't find the next speaker agent in the dialogue. Next speaker: {self._next_speaker}. Agents: {self._involved_agents}"
            raise CouldntDetermineNextSpeakerError(error_message)

        return agent_who_will_speak_now

    def _add_relevant_memories_regarding_interlocutors(
        self, user_content, agent_who_will_speak_now
    ):
        user_content += f"Summary of relevant context from {agent_who_will_speak_now.get_name()}'s memory:\n"

        index, memories_raw_data = MemoriesDatabaseLoader(
            agent_who_will_speak_now.get_name()
        ).load()

        memories_database_querier = MemoriesDatabaseQuerier(
            agent_who_will_speak_now.get_name(),
            self._current_timestamp,
            memories_raw_data,
            index,
        )

        for agent in self._involved_agents:
            if agent != agent_who_will_speak_now:
                relevant_memories = memories_database_querier.query(
                    f"What is {agent_who_will_speak_now.get_name()}'s relationship with {agent.get_name()}?",
                    20,
                )

                user_content += " ".join(relevant_memories)

        return user_content

    def _produce_line_of_dialogue(self):
        messages = []

        messages.append(
            {
                "role": SYSTEM_ROLE,
                "content": PRODUCE_LINE_OF_DIALOGUE_GPT_SYSTEM_CONTENT,
            }
        )

        agent_who_will_speak_now = self._determine_agent_who_will_speak_now()

        user_content = ""

        if agent_who_will_speak_now.get_character_summary() is not None:
            user_content += f"{agent_who_will_speak_now.get_character_summary()}\n"

        user_content = self._add_involved_agents_status(user_content)

        user_content = self._add_relevant_memories_regarding_interlocutors(
            user_content, agent_who_will_speak_now
        )

        # Now add the dialogue history
        user_content = self._add_dialogue_history(user_content)

        # Prompt the AI model to write a line for the dialogue.
        user_content += f"\n{agent_who_will_speak_now.get_name()} is going to speak now. What does {agent_who_will_speak_now.get_name()} say?"

        messages.append({"role": USER_ROLE, "content": user_content})

        functions = []
        append_single_parameter_function(
            functions,
            WRITE_LINE_OF_DIALOGUE_FUNCTION_NAME,
            WRITE_LINE_OF_DIALOGUE_FUNCTION_DESCRIPTION,
            LINE_OF_DIALOGUE_PARAMETER_NAME,
            "string",
            LINE_OF_DIALOGUE_PARAMETER_DESCRIPTION,
        )

        response = (
            agent_who_will_speak_now.get_request_response_from_ai_model_function()(
                messages,
                functions,
                {"name": WRITE_LINE_OF_DIALOGUE_FUNCTION_NAME},
                GPT_4,
            )
        )

        # We must separate player responses from AI model responses.
        if (
            self._player_agent
            and agent_who_will_speak_now.get_name() == self._player_agent.get_name()
        ):
            self._dialogue_history.append(get_message_from_gpt_response(response))
        elif response.get("choices"):
            function_arguments = load_arguments_of_message_with_function_call(
                get_message_from_gpt_response(response)
            )

            self._dialogue_history.append(
                {
                    "role": USER_ROLE,
                    "content": function_arguments.get(LINE_OF_DIALOGUE_PARAMETER_NAME),
                }
            )
        else:
            raise ValueError(
                f"Didn't know how to handle response {response}\nNext speaker: {self._next_speaker}\nAgent who will speak now: {agent_who_will_speak_now}"
            )

    def _add_characters_involved_in_conversation(self, user_content):
        user_content += "\nCharacters involved in conversation: " + ", ".join(
            [agent.get_name() for agent in self._involved_agents]
        )

        return user_content

    def _add_agent_statuses(self, user_content):
        for agent in self._involved_agents:
            user_content += f"\n{agent.get_name()}'s status: {agent.get_status()}"

        return user_content

    def _add_user_content_for_who_will_speak(self):
        user_content = format_timestamp_for_prompt(self._current_timestamp)

        user_content = self._add_characters_involved_in_conversation(user_content)

        user_content = self._add_agent_statuses(user_content)

        user_content = self._add_reason_for_conversation(user_content)

        return user_content

    def _request_from_ai_model_who_will_speak_next(
        self, messages, functions, function_name, parameter_name
    ):
        response = self._request_response_from_ai_model_with_functions_function(
            messages,
            functions,
            {"name": function_name},
            GPT_3_5,
        )

        function_arguments = load_arguments_of_message_with_function_call(
            get_message_from_gpt_response(response)
        )

        return function_arguments.get(parameter_name)

    def _determine_next_speaker(self) -> str:
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

        user_content = self._add_user_content_for_who_will_speak()

        user_content += "\n\nWhat is the name of the name of the character who will utter the next line of dialogue?"
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

        return self._request_from_ai_model_who_will_speak_next(
            messages,
            functions,
            DETERMINE_WHO_WILL_SPEAK_NEXT_FUNCTION_NAME,
            CHARACTER_WHO_WILL_SPEAK_NEXT_PARAMETER_NAME,
        )

    def _determine_who_is_going_to_speak_first(self):
        messages = []

        messages.append(
            {
                "role": SYSTEM_ROLE,
                "content": WHO_WILL_SPEAK_FIRST_GPT_SYSTEM_CONTENT,
            }
        )

        user_content = self._add_user_content_for_who_will_speak()

        user_content += "\n\nWhat is the name of the name of the character who will utter the first line of dialogue?"

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

        return self._request_from_ai_model_who_will_speak_next(
            messages,
            functions,
            DETERMINE_WHO_WILL_SPEAK_FIRST_FUNCTION_NAME,
            CHARACTER_WHO_WILL_SPEAK_FIRST_PARAMETER_NAME,
        )

    def _ensure_next_speaker_isnt_last_one(self):
        determined_next_speaker = self._determine_next_speaker()

        # we would never want to have the same person talking twice in a row.
        if determined_next_speaker.lower() == self._next_speaker.lower():
            for agent in self._involved_agents:
                if agent.get_name().lower() != determined_next_speaker.lower():
                    determined_next_speaker = agent.get_name()
                    break

        self._next_speaker = determined_next_speaker

    def perform_dialogue(self) -> list:
        """Performs a dialogue given the initial context passed during the initialization of this class.
        This dialogue will continue until the AI model stops the dialogue by using the function 'stop_dialogue',
        passed as an option through every request.

        Returns:
            list: the list of messages containing every line of dialogue.
        """
        should_dialogue_continue = True

        while should_dialogue_continue:
            self._produce_line_of_dialogue()

            print(self._dialogue_history[-1:])

            if self._determine_if_dialogue_should_end():
                should_dialogue_continue = False

            if should_dialogue_continue:
                self._ensure_next_speaker_isnt_last_one()

        return self._dialogue_history
