from string_utils import replace_spaces_with_underscores


def get_base_memories_full_path(agent_name: str):
    return f"assets/base_memories/{replace_spaces_with_underscores(agent_name.lower())}_memories.ann"


def get_base_memories_json_full_path(agent_name: str):
    return f"assets/base_memories/{replace_spaces_with_underscores(agent_name.lower())}_memories.json"


def get_seed_memories_full_path(agent_name: str):
    return f"assets/seed_memories/{replace_spaces_with_underscores(agent_name.lower())}_seed_memories.txt"


def get_simulation_facts_full_path(simulation_name: str):
    return f"assets/simulations/{replace_spaces_with_underscores(simulation_name.lower())}_facts.ann"


def get_simulation_facts_json_full_path(simulation_name: str):
    return f"assets/simulations/{replace_spaces_with_underscores(simulation_name.lower())}_facts.json"


def get_seed_facts_of_simulation_full_path(simulation_name: str):
    return f"assets/simulations/{replace_spaces_with_underscores(simulation_name.lower())}_seed_facts.txt"


def get_character_summary_full_path(agent_name: str):
    return f"assets/character_summaries/{replace_spaces_with_underscores(agent_name.lower())}_character_summary.txt"
