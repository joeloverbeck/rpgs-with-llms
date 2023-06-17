from datetime import datetime


def format_timestamp_for_prompt(timestamp: datetime):
    hour_format = timestamp.strftime("%I").lstrip("0")

    return timestamp.strftime(f"It is %B %d, %Y, {hour_format}:%M %p")
