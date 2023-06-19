#!/usr/bin/env python3
from datetime import datetime
from agents.agent import Agent
from console_output.messages import output_colored_message
from dialogue.conversation_state import ConversationState
from dialogue.dialogue_coordinator import DialogueCoordinator
from files.loading import load_text_file
from input.confirmation import request_confirmation
from llms.gpt_responder import GPTResponder
from llms.user_responder import UserResponder
from paths.full_paths import get_character_summary_full_path


def main():
    current_timestamp = datetime(2023, 11, 4, 19, 10)

    involved_agents = []

    gpt_responder = GPTResponder()
    user_responder = UserResponder()

    leire = Agent("Leire", user_responder)
    leire.set_status(
        "Leire is disturbed about having found herself in a fantasy world after being run over by a truck. She's desperate for money so she can crash in an inn."
    )
    leire.set_character_summary(
        load_text_file(get_character_summary_full_path(leire.get_name()))
    )

    involved_agents.append(leire)

    elysia = Agent("Elysia Starbinder", user_responder)
    elysia_status = "Elysia Starbinder is walking around town with her pal Eolan, while planning their next hunt, when they are accosted by a disturbed-looking woman."
    elysia.set_status(elysia_status)
    elysia.set_character_summary(
        load_text_file(get_character_summary_full_path(elysia.get_name()))
    )

    involved_agents.append(elysia)

    eolan = Agent("Eolan", user_responder)
    eolan_status = "Eolan is walking around town with his pal Elysia Starbinder, while planning their next hunt, when they are accosted by a disturbed-looking woman."
    eolan.set_status(eolan_status)
    eolan.set_character_summary(
        load_text_file(get_character_summary_full_path(eolan.get_name()))
    )

    involved_agents.append(eolan)

    messages = DialogueCoordinator(
        ConversationState(
            current_timestamp,
            "Leire, disturbed, confused and despairing after having been transported to a fantasy world, has approached Eolan and Elysia to rob them.",
            leire,
            involved_agents,
        ),
        request_confirmation("Do you want to speak first?"),
        user_responder,
    ).perform_dialogue()

    # print the messages
    for message in messages:
        output_colored_message("light_yellow", message["content"])


if __name__ == "__main__":
    main()
