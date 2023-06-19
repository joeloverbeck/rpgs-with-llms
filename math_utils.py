import math

from defines.defines import SCORE_ALPHA, SCORE_BETA, SCORE_GAMMA
from errors import CurrentTimestampIsLaterThanAccessTimestampError, ValueOutOfRangeError


def calculate_recency(current_timestamp, access_timestamp, decay_rate) -> float:
    """Calculates how recent an entry is according to the current and access timestamps,
    and depending on the decay rate.

    Args:
        current_timestamp (datetime): the current timestamp of an entry.
        access_timestamp (datetime): the last access timestamp of an entry.
        decay_rate (float): the decay rate to calculate the recency.

    Returns:
        float: the calculated recency of the entry.

    Raises:
        CurrentTimestampIsLaterThanAccessTimestampError: If the current_timestamp is not later than the access_timestamp.
    """
    if current_timestamp < access_timestamp:
        raise CurrentTimestampIsLaterThanAccessTimestampError(
            f"The current timestamp should be later than the access timestamp.\nCurrent timestamp: {current_timestamp}\nAccess timestamp: {access_timestamp}"
        )

    time_difference = current_timestamp - access_timestamp
    time_difference_in_seconds = time_difference.total_seconds()

    return math.exp(-decay_rate * time_difference_in_seconds)


def normalize_value(value: int) -> float:
    """Normalizes a value in the range 1-10.

    Args:
        value (int): the value to normalize.

    Returns:
        float: the normalized value.

    Raises:
        ValueOutOfRangeError: If the input value is not in the range 1-10.
    """
    if not 1 <= value <= 10:
        raise ValueOutOfRangeError(
            "The input value is out of range. It should be in the range 1-10."
        )

    return (value - 1) / 9


def calculate_score(
    relevance: float,
    recency: float,
    importance: float,
    alpha=SCORE_ALPHA,
    beta=SCORE_BETA,
    gamma=SCORE_GAMMA,
):
    return alpha * relevance + beta * recency + gamma * importance
