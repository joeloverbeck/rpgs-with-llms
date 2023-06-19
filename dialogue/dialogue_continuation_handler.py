from datetime_utils import format_timestamp_for_prompt
from defines.defines import GPT_3_5, SYSTEM_ROLE, USER_ROLE
from dialogue.conversation_state import ConversationState
from dialogue.dialogue_history_handler import DialogueHistoryHandler
from dialogue.prompting import add_involved_agents_status, add_reason_for_conversation
from input.confirmation import request_confirmation
from llms.functions import append_single_parameter_function
from llms.interface import AIModelInterface
from llms.messages import (
    get_message_from_gpt_response,
    load_arguments_of_message_with_function_call,
)

SHOULD_STOP_DIALOGUE_GPT_SYSTEM_CONTENT = "I am ShouldStopDialogueDeterminerGPT. I have the responsibility of determining if the ongoing dialogue should realistically "
SHOULD_STOP_DIALOGUE_GPT_SYSTEM_CONTENT += (
    "end now, given the context of the conversation and the latest lines of dialogue."
)
SHOULD_STOP_DIALOGUE_FUNCTION_NAME = "should_stop_dialogue"
SHOULD_STOP_DIALOGUE_FUNCTION_DESCRIPTION = "Determines if the dialogue has reached a natural conclusion, given the context of the conversation and "
SHOULD_STOP_DIALOGUE_FUNCTION_DESCRIPTION += "the latest lines of dialogue."
SHOULD_STOP_DIALOGUE_PARAMETER_NAME = "should_stop_dialogue"
SHOULD_STOP_DIALOGUE_PARAMETER_DESCRIPTION = "Whether or not the dialogue has reached a natural conclusion, given the context of the conversation and "
SHOULD_STOP_DIALOGUE_PARAMETER_DESCRIPTION += "the latest lines of dialogue."


class DialogueContinuationHandler:
    """Class that handles whether an ongoing dialogue should continue."""

    def __init__(
        self,
        conversation_state: ConversationState,
        dialogue_history_handler: DialogueHistoryHandler,
        ai_model_interface: AIModelInterface,
    ):
        """Creates an instance of the class DialogueContinuationHandler.

        Args:
            conversation_state (ConversationState): the state of the conversation.
            dialogue_history_handler (DialogueHistoryHandler): the handler of the dialogue history.
            ai_model_interface (AIModelInterface): the interface to request responses from the AI Model.
        """
        self._should_dialogue_continue = True

        self._conversation_state = conversation_state
        self._dialogue_history_handler = dialogue_history_handler
        self._ai_model_interface = ai_model_interface

    def should_dialogue_continue(self) -> bool:
        """Returns whether the dialogue should continue.

        Returns:
            bool: whether the dialogue should continue.
        """
        return self._should_dialogue_continue

    def _determine_user_content_to_determine_if_dialogue_should_end(self) -> str:
        """Determines what should be added to the prompt that will be sent to the AI model
        so that it determines whether or not the dialogue should end.

        Returns:
            str: the user content that will be sent in the prompt to the AI model.
        """
        user_content = ""

        user_content += f"{format_timestamp_for_prompt(self._conversation_state.get_current_timestamp())}\n"

        user_content = add_involved_agents_status(
            user_content, self._conversation_state.get_involved_agents()
        )

        user_content = add_reason_for_conversation(
            user_content, self._conversation_state.get_reason_for_conversation()
        )

        user_content = self._dialogue_history_handler.add_dialogue_history_for_prompt(
            user_content
        )

        user_content += "\nGiven the context and the latest lines of dialogue, should the dialogue end now "
        user_content += "because it has reached a natural conclusion?"

        return user_content

    def determine_if_dialogue_should_end(self):
        """Given the current state of the dialogue, this function delegates to the AI model
        the decision of whether or not the dialogue should end now.
        """
        messages = []

        messages.append(
            {
                "role": SYSTEM_ROLE,
                "content": SHOULD_STOP_DIALOGUE_GPT_SYSTEM_CONTENT,
            }
        )

        messages.append(
            {
                "role": USER_ROLE,
                "content": self._determine_user_content_to_determine_if_dialogue_should_end(),
            }
        )

        functions = []
        append_single_parameter_function(
            functions,
            SHOULD_STOP_DIALOGUE_FUNCTION_NAME,
            SHOULD_STOP_DIALOGUE_FUNCTION_DESCRIPTION,
            SHOULD_STOP_DIALOGUE_PARAMETER_NAME,
            "boolean",
            SHOULD_STOP_DIALOGUE_PARAMETER_DESCRIPTION,
        )

        message = get_message_from_gpt_response(
            self._ai_model_interface.request_response_using_functions(
                messages,
                functions,
                {"name": SHOULD_STOP_DIALOGUE_FUNCTION_NAME},
                GPT_3_5,
            )
        )

        # Note: the message could have come from the user, for example in the case
        # that the user is testing prompts.

        if message.get("function_call"):
            function_arguments = load_arguments_of_message_with_function_call(message)

            should_dialogue_stop = function_arguments.get(
                SHOULD_STOP_DIALOGUE_PARAMETER_NAME
            )
        else:
            should_dialogue_stop = bool(message["content"].lower().strip() == "true")

        # Offer the user the opportunity to trump the AI's decision.
        if should_dialogue_stop and request_confirmation(
            "The AI model has decided that the dialogue should end now. Do you want it to continue?"
        ):
            should_dialogue_stop = False

        if should_dialogue_stop:
            self._should_dialogue_continue = False
