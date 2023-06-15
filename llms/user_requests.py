import random
import string
import time
from defines.defines import GPT_3_5
from errors import InvalidParameterError


def request_response_from_user(
    messages: list[dict], _functions=None, _function_call="auto", _model=GPT_3_5
) -> dict:
    """Gets a response from user input.

    Args:
        _messages (list[dict]): the list of messages that will be sent to the user.

    Returns:
        dict: the response returned from the user.
    """

    if not isinstance(messages, list):
        error_message = f"The function {request_response_from_user.__name__} expected 'messages' to be a list, but it was: {messages}"
        raise InvalidParameterError(error_message)

    # Prompt user with the content of the last message
    user_input = input(f"{messages[-1]['content']}\nUser input: ")

    # Create a random ID for the response
    id_string = "chatcmpl-" + "".join(
        random.choices(string.ascii_letters + string.digits, k=24)
    )

    # Create a response in the same format as the AI model
    response = {
        "id": id_string,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": _model,
        "usage": {
            "prompt_tokens": len(messages[-1]["content"].split()),
            "completion_tokens": len(user_input.split()),
            "total_tokens": len(messages[-1]["content"].split())
            + len(user_input.split()),
        },
        "choices": [
            {
                "message": {"role": "user", "content": user_input},
                "finish_reason": "stop",
                "index": 0,
            }
        ],
    }

    return response
