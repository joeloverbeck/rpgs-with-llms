from defines.defines import GPT_3_5


class DialogueRequester:
    def __init__(
        self,
        messages: list,
        functions: list | None,
        request_response_from_ai_model_function,
        function_call="auto",
        model=GPT_3_5,
    ):
        self._messages = messages
        self._functions = functions
        self._request_response_from_ai_model_function = (
            request_response_from_ai_model_function
        )
        self._function_call = function_call
        self._model = model

    def request_response(self) -> dict:
        return self._request_response_from_ai_model_function(
            self._messages, self._functions, self._function_call, self._model
        )
