import json

from errors import FailedToExtractArgumentsFromFunctionCallError


def get_message_from_gpt_response(response: dict):
    return response["choices"][0]["message"]


def load_arguments_of_message_with_function_call(message: dict):
    if not message.get("function_call"):
        error_message = f"The function {load_arguments_of_message_with_function_call.__name__} expected the message to have received a function call, "
        error_message += f"but instead it was: {message}"
        raise ValueError(error_message)

    try:
        return json.loads(message["function_call"]["arguments"])
    except json.JSONDecodeError as exception:
        error_message = f"Failed to extract arguments from function call given message: {message}\nError: {exception}"
        raise FailedToExtractArgumentsFromFunctionCallError(
            error_message
        ) from exception
