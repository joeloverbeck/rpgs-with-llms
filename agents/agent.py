class Agent:
    def __init__(self, name, request_response_from_ai_model_function):
        self._name = name
        self._request_response_from_ai_model_function = (
            request_response_from_ai_model_function
        )

        self._status = None
        self._character_summary = None

    def get_name(self):
        return self._name

    def get_request_response_from_ai_model_function(self):
        return self._request_response_from_ai_model_function

    def get_status(self):
        return self._status

    def set_status(self, status):
        self._status = status

    def get_character_summary(self):
        return self._character_summary

    def set_character_summary(self, character_summary):
        self._character_summary = character_summary
