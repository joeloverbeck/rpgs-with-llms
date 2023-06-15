"""This module contains functions related to requesting responses from AI models.
"""
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential
from defines.defines import (
    GPT_3_5,
)
from errors import InvalidParameterError

# Read API key from file
with open("api_key.txt", "r", encoding="utf8") as file:
    openai.api_key = file.read().strip()


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def request_response_from_ai_model(
    messages: list[dict], functions=None, function_call="auto", model=GPT_3_5
) -> dict:
    """Tries to get a response from an AI model.

    Args:
        messages (list[dict]): the list of messages that will be sent to the AI model.

    Returns:
        dict: the response returned from the AI model.
    """
    if not isinstance(messages, list):
        error_message = f"The function {request_response_from_ai_model.__name__} expected 'messages' to be a list, but it was: {messages}"
        raise InvalidParameterError(error_message)

    response = openai.ChatCompletion.create(
        model=model,
        temperature=1,
        messages=messages,
        max_tokens=2048,
        functions=functions,
        function_call=function_call,
    )

    return response
