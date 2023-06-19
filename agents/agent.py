from llms.interface import AIModelInterface


class Agent:
    def __init__(self, name: str, ai_model_interface: AIModelInterface):
        self._name = name
        self._ai_model_interface = ai_model_interface

        self._status = None
        self._character_summary = None

    def get_name(self):
        return self._name

    def get_ai_model_interface(self):
        return self._ai_model_interface

    def get_status(self):
        return self._status

    def set_status(self, status):
        self._status = status

    def get_character_summary(self):
        return self._character_summary

    def set_character_summary(self, character_summary):
        self._character_summary = character_summary
