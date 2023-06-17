from defines.defines import GPT_3_5
from errors import InvalidParameterError
from llms.responses import create_response_in_gpt_format


def request_response_from_user(
    messages: list[dict], _functions=None, _function_call="auto", model=GPT_3_5
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

    return create_response_in_gpt_format(user_input, messages, model)
