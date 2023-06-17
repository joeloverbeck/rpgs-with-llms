def get_message_from_gpt_response(response: dict):
    return response["choices"][0]["message"]
