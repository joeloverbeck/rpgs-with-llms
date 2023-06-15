from defines.defines import AGENTS_DIRECTORY_PATH, CHARACTER_ATTRIBUTES_DATABASE_NAME


def get_base_character_attributes_full_path(agent_name):
    return (
        f"{AGENTS_DIRECTORY_PATH}/{agent_name}_{CHARACTER_ATTRIBUTES_DATABASE_NAME}.ann"
    )
