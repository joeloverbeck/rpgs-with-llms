"""This module contains functions related to requesting responses from AI models.
"""
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential
from defines.defines import (
    DEFAULT_TEMPERATURE,
    GPT_3_5,
    MAX_TOKENS,
)
from errors import InvalidParameterError, PromptTooBigError

# Read API key from file
with open("api_key.txt", "r", encoding="utf8") as file:
    openai.api_key = file.read().strip()


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def request_ai_response_with_functions(
    messages: list[dict], functions: list[dict], function_call="auto", model=GPT_3_5
) -> dict:
    """Tries to get a response from an AI model. In this variant, the use of functions is expected
    by the AI model.

    Args:
        messages (list[dict]): the list of messages that will be sent to the AI model.
        functions (list[dict]): the list of functions that the AI model will have available.
        function_call (str): whether the AI model should choose to use the functions or not.
            It is required by the OpenAI API. The default value of 'auto' means that it will use any
            of the available functions when it considers it necessary.
        model (str): what AI model will be used.

    Returns:
        dict: the response returned from the AI model.
    """
    if not isinstance(messages, list):
        error_message = f"The function {request_ai_response_with_functions.__name__} expected 'messages' to be a list, but it was: {messages}"
        raise InvalidParameterError(error_message)
    if functions is None:
        error_message = f"The function {request_ai_response_with_functions.__name__} expected 'functions' not to be None."
        raise InvalidParameterError(error_message)

    try:
        response = openai.ChatCompletion.create(
            model=model,
            temperature=DEFAULT_TEMPERATURE,
            messages=messages,
            max_tokens=MAX_TOKENS,
            functions=functions,
            function_call=function_call,
        )
    except openai.InvalidRequestError as exception:
        raise PromptTooBigError(
            f"GPT refused a request because the prompt was too big.\nError: {exception}\nLast message: {messages[-1:]}"
        ) from exception

    return response


@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def request_ai_response(messages: list[dict], model=GPT_3_5) -> dict:
    """Tries to get a response from an AI model.

    Args:
        messages (list[dict]): the list of messages that will be sent to the AI model.
        model (str): what AI model will be used.

    Returns:
        dict: the response returned from the AI model.
    """
    if not isinstance(messages, list):
        error_message = f"The function {request_ai_response.__name__} expected 'messages' to be a list, but it was: {messages}"
        raise InvalidParameterError(error_message)

    response = openai.ChatCompletion.create(
        model=model,
        temperature=DEFAULT_TEMPERATURE,
        messages=messages,
        max_tokens=MAX_TOKENS,
    )

    return response
