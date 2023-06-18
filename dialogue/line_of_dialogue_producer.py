from datetime import datetime
from agents.agent import Agent
from datetime_utils import format_timestamp_for_prompt
from defines.defines import GPT_4, SYSTEM_ROLE, USER_ROLE
from dialogue.dialogue_history_handler import DialogueHistoryHandler
from dialogue.next_speaker_selector import NextSpeakerSelector
from dialogue.prompting import (
    add_involved_agents_status,
    add_reason_for_conversation,
    add_relevant_memories_regarding_interlocutors,
)
from dialogue.speaking_order import determine_agent_who_will_speak_now
from llms.functions import append_single_parameter_function
from llms.messages import (
    get_message_from_gpt_response,
    load_arguments_of_message_with_function_call,
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


class LineOfDialogueProducer:
    def __init__(
        self,
        current_timestamp: datetime,
        reason_for_conversation: str,
        player_agent: Agent,
        involved_agents: list[Agent],
        next_speaker_selector: NextSpeakerSelector,
    ):
        self._current_timestamp = current_timestamp
        self._reason_for_conversation = reason_for_conversation
        self._player_agent = player_agent
        self._involved_agents = involved_agents
        self._next_speaker_selector = next_speaker_selector

    def _separate_player_response_from_ai_model_response(
        self, agent_who_will_speak_now: Agent, response: dict
    ) -> dict:
        """Handles the response gotten either from the player or from an AI model.
        The AI model will return a function call, while the player will return
        a fully-fledged message to store in the dialogue history.

        Args:
            agent_who_will_speak_now (Agent): the agent whose line of dialogue is contained in 'response'
            response (dict): the response either from the user or from the AI model.

        Raises:
            ValueError: if the contents of 'response' were unexpected.
        """
        if response.get("choices"):
            # Could be the case that function call isn't set
            message = get_message_from_gpt_response(response)

            if message.get("function_call"):
                # This message has been produced by the AI model, by using the passed function.
                function_arguments = load_arguments_of_message_with_function_call(
                    message
                )

                print(f"{function_arguments.get(LINE_OF_DIALOGUE_PARAMETER_NAME)}\n")

                return {
                    "role": USER_ROLE,
                    "content": function_arguments.get(LINE_OF_DIALOGUE_PARAMETER_NAME),
                }

            # This message has been produced by the user.
            return message

        error_message = f"Didn't know how to handle response {response}\nNext speaker: {self._next_speaker_selector.get_next_speaker()}"
        error_message += f"\nAgent who will speak now: {agent_who_will_speak_now}"
        raise ValueError(error_message)

    def _determine_user_content_for_producing_line_of_dialogue(
        self,
        agent_who_will_speak_now: Agent,
        dialogue_history_handler: DialogueHistoryHandler,
    ) -> str:
        """Determines part of the text that will end up in the prompt sent to the AI model,
        who will produce a line of dialogue based on the prompt.

        Args:
            agent_who_will_speak_now (Agent): the agent chosen to speak now.

        Returns:
            str: part of the text that will end up in the prompt to be sent to the AI model.
        """
        user_content = ""

        if agent_who_will_speak_now.get_character_summary() is not None:
            user_content += f"{agent_who_will_speak_now.get_character_summary()}\n"

        user_content += f"{format_timestamp_for_prompt(self._current_timestamp)}\n"

        user_content = add_involved_agents_status(user_content, self._involved_agents)

        user_content = add_reason_for_conversation(
            user_content, self._reason_for_conversation
        )

        user_content = add_relevant_memories_regarding_interlocutors(
            self._current_timestamp,
            user_content,
            agent_who_will_speak_now,
            self._involved_agents,
        )

        # Now add the dialogue history
        user_content = dialogue_history_handler.add_dialogue_history_for_prompt(
            user_content
        )

        # Prompt the AI model to write a line for the dialogue.
        user_content += f"\n{agent_who_will_speak_now.get_name()} is going to speak now. What does {agent_who_will_speak_now.get_name()} say?"

        return user_content

    def produce_line_of_dialogue(
        self, dialogue_history_handler: DialogueHistoryHandler
    ) -> dict:
        """Delegates to either the user (if a player agent is set) or an AI model producing a line of dialogue."""
        messages = []

        messages.append(
            {
                "role": SYSTEM_ROLE,
                "content": PRODUCE_LINE_OF_DIALOGUE_GPT_SYSTEM_CONTENT,
            }
        )

        agent_who_will_speak_now = determine_agent_who_will_speak_now(
            self._next_speaker_selector.get_next_speaker(), self._involved_agents
        )

        messages.append(
            {
                "role": USER_ROLE,
                "content": self._determine_user_content_for_producing_line_of_dialogue(
                    agent_who_will_speak_now, dialogue_history_handler
                ),
            }
        )

        functions = []
        append_single_parameter_function(
            functions,
            WRITE_LINE_OF_DIALOGUE_FUNCTION_NAME,
            WRITE_LINE_OF_DIALOGUE_FUNCTION_DESCRIPTION,
            LINE_OF_DIALOGUE_PARAMETER_NAME,
            "string",
            LINE_OF_DIALOGUE_PARAMETER_DESCRIPTION,
        )

        return self._separate_player_response_from_ai_model_response(
            agent_who_will_speak_now,
            agent_who_will_speak_now.get_request_response_from_ai_model_function()(
                messages,
                functions,
                {"name": WRITE_LINE_OF_DIALOGUE_FUNCTION_NAME},
                GPT_4,
            ),
        )
