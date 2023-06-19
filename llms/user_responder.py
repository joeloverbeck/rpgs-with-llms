from typing import List
from llms.interface import AIModelInterface
from llms.responses import create_response_in_gpt_format


class UserResponder(AIModelInterface):
    def _request_response_from_user(self, messages, model):
        if not isinstance(messages, list):
            error_message = f"The function {self.request_response_using_functions.__name__} expected 'messages' to be a list, but it was: {messages}"
            raise TypeError(error_message)

        # Prompt user with the content of the last message
        user_input = input(f"{messages[-1]['content']}\nUser input: ")

        return create_response_in_gpt_format(user_input, messages, model)

    def request_response_using_functions(
        self,
        messages: List[dict],
        _functions: List[dict],
        _function_call: str,
        model: str,
    ) -> dict:
        """Gets a response from user input.

        Args:
            _messages (list[dict]): the list of messages that will be sent to the user.

        Returns:
            dict: the response returned from the user.
        """
        return self._request_response_from_user(messages, model)

    def request_response(self, messages: List[dict], model: str) -> dict:
        return self._request_response_from_user(messages, model)
