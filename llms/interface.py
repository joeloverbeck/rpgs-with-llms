from abc import ABC, abstractmethod
from typing import List


class AIModelInterface(ABC):
    @abstractmethod
    def request_response_using_functions(
        self,
        messages: List[dict],
        functions: List[dict],
        function_call: str,
        model: str,
    ) -> dict:
        pass

    @abstractmethod
    def request_response(self, messages: List[dict], model: str) -> dict:
        pass
