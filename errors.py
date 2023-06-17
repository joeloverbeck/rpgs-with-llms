class InvalidParameterError(Exception):
    pass


class FailedToReceiveFunctionCallFromAiModelError(Exception):
    pass


class UnableToSaveVectorDatabaseError(Exception):
    pass


class DisparityBetweenDatabasesError(Exception):
    pass


class CurrentTimestampIsLaterThanAccessTimestampError(Exception):
    pass


class ValueOutOfRangeError(Exception):
    pass
