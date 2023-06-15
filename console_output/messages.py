from termcolor import colored


def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }

    for message in messages:
        formatted_message = ""
        if message["role"] == "system":
            formatted_message = f"system: {message['content']}\n"
        elif message["role"] == "user":
            formatted_message = f"user: {message['content']}\n"
        elif message["role"] == "assistant" and message.get("function_call"):
            formatted_message = f"assistant: {message['function_call']}\n"
        elif message["role"] == "assistant" and not message.get("function_call"):
            formatted_message = f"assistant: {message['content']}\n"
        elif message["role"] == "function":
            formatted_message = f"function ({message['name']}): {message['content']}\n"

        print(
            colored(formatted_message, role_to_color[message["role"]], attrs=["bold"])
        )
