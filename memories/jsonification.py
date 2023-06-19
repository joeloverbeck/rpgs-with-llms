from datetime import datetime
import json
import os

from defines.defines import DECAY_RATE, GPT_3_5
from errors import FailedToReceiveFunctionCallFromAiModelError
from llms.interface import AIModelInterface
from math_utils import calculate_recency, normalize_value


def append_to_previous_json_memories_if_necessary(json_filename, memories):
    """This function will prevent squashing the previous json memories file
    if one exists, because it will load the contents of that file
    and add the new memories to that raw mapping.

    Args:
        json_filename (str): the full path to the json file
        memories (dict): new memories that need to be saved to disk

    Returns:
        dict: either the original memories or the previous memories + the new ones
    """
    # Remember to load all the memories in the json file,
    # or else you'll just overwrite the file with "create_json_file"
    if os.path.isfile(json_filename):
        with open(json_filename, "r", encoding="utf8") as json_file:
            raw_text_mapping = json.load(json_file)

        for index, entry in memories.items():
            raw_text_mapping[index] = entry

        return raw_text_mapping

    return memories


def create_memory_dictionary(
    memory_description: str,
    current_timestamp: datetime,
    ai_model_interface: AIModelInterface,
):
    """Creates a memory dict for the memory description passed

    Args:
        memory_description (str): the description of the memory
        current_timestamp (datetime): the current timestamp

    Returns:
        dict: the data asociated with the memory, to store in a json file
    """
    most_recent_access_timestamp = current_timestamp

    recency = calculate_recency(
        current_timestamp, most_recent_access_timestamp, DECAY_RATE
    )

    messages = []

    system_content = "I am MemoryImportanceJudgeGPT. I have the responsibility of rating memories from 1 to 10 according to their importance."
    messages.append(
        {
            "role": "system",
            "content": system_content,
        }
    )

    functions = []
    functions.append(
        {
            "name": "get_importance_rating_for_memory",
            "description": "Gets the importance rating for a memory, from 1 to 10.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rating": {
                        "type": "integer",
                        "description": "A rating from 1 to 10 of the importance of the memory.",
                    }
                },
                "required": ["rating"],
            },
        }
    )

    user_prompt = "On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) "
    user_prompt += "and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely importance "
    user_prompt += "of the following piece of memory."
    user_prompt += f" Memory: {memory_description}"

    messages.append({"role": "user", "content": user_prompt})

    importance_response = ai_model_interface.request_response_using_functions(
        messages,
        functions,
        function_call={"name": "get_importance_rating_for_memory"},
        model=GPT_3_5,
    )

    message = importance_response["choices"][0]["message"]

    if not message.get("function_call"):
        error_message = f"In the function {create_memory_dictionary.__name__}, I failed to receive the function call with the rating from GPT: {message}"
        raise FailedToReceiveFunctionCallFromAiModelError(error_message)

    function_arguments = json.loads(message["function_call"]["arguments"])

    normalized_importance = normalize_value(function_arguments.get("rating"))

    # We must create a whole memory dict.
    return {
        "description": memory_description,
        "creation_timestamp": current_timestamp.isoformat(),
        "most_recent_access_timestamp": most_recent_access_timestamp.isoformat(),
        "recency": recency,
        "importance": normalized_importance,
    }


def format_json_memory_data_for_python(memories_raw_data):
    for memory_key in memories_raw_data:
        memories_raw_data[memory_key] = {
            "description": memories_raw_data[memory_key]["description"],
            "creation_timestamp": datetime.fromisoformat(
                memories_raw_data[memory_key]["creation_timestamp"]
            ),
            "most_recent_access_timestamp": datetime.fromisoformat(
                memories_raw_data[memory_key]["most_recent_access_timestamp"]
            ),
            "recency": memories_raw_data[memory_key]["recency"],
            "importance": memories_raw_data[memory_key]["importance"],
        }

    return memories_raw_data


def format_python_memory_data_for_json(memories_raw_data):
    for memory_key in memories_raw_data:
        creation_timestamp = (
            memories_raw_data[memory_key]["creation_timestamp"].isoformat()
            if isinstance(memories_raw_data[memory_key]["creation_timestamp"], datetime)
            else memories_raw_data[memory_key]["creation_timestamp"]
        )

        most_recent_access_timestamp = (
            memories_raw_data[memory_key]["most_recent_access_timestamp"].isoformat()
            if isinstance(
                memories_raw_data[memory_key]["most_recent_access_timestamp"], datetime
            )
            else memories_raw_data[memory_key]["most_recent_access_timestamp"]
        )

        memories_raw_data[memory_key] = {
            "description": memories_raw_data[memory_key]["description"],
            "creation_timestamp": creation_timestamp,
            "most_recent_access_timestamp": most_recent_access_timestamp,
            "recency": memories_raw_data[memory_key]["recency"],
            "importance": memories_raw_data[memory_key]["importance"],
        }

    return memories_raw_data
