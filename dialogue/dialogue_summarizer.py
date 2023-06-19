from defines.defines import GPT_4
from errors import InvalidParameterError
from llms.interface import AIModelInterface


class DialogueSummarizer:
    def __init__(self, messages: list, ai_model_interface: AIModelInterface):
        if not isinstance(messages, list):
            error_message = f"The init function of {DialogueSummarizer.__name__} required 'messages' to be a list, but it was: {messages}"
            raise InvalidParameterError(error_message)

        self._messages = messages

        self._ai_model_interface = ai_model_interface

    def summarize(self):
        copied_messages = list(self._messages)

        system_content = "I am DialogueSummarizerGPT. I have the responsibility of summarizing a dialogue held between two or more characters, "
        system_content += (
            "making sure to note the most important points of the dialogue."
        )
        copied_messages.append(
            {
                "role": "system",
                "content": system_content,
            }
        )

        user_content = "Please summarize the previous dialogue."
        copied_messages.append({"role": "user", "content": user_content})

        return self._ai_model_interface.request_response(copied_messages, model=GPT_4)
