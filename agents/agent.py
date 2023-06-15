class Agent:
    def __init__(self, name, request_response_from_ai_model_function):
        self._name = name
        self._request_response_from_ai_model_function = (
            request_response_from_ai_model_function
        )

    def get_name(self):
        return self._name

    def get_request_response_from_ai_model_function(self):
        return self._request_response_from_ai_model_function
