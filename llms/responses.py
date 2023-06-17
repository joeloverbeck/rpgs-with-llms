import random
import string
import time


def create_response_in_gpt_format(user_input, messages, model):
    # Create a random ID for the response
    id_string = "chatcmpl-" + "".join(
        random.choices(string.ascii_letters + string.digits, k=24)
    )

    # Create a response in the same format as the AI model
    return {
        "id": id_string,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
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
