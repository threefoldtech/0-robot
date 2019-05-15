class BadActionArgumentError(Exception):
    """
    Error return when the argument pass when trying to schedule an action
    doesn't match with the method signature
    """

    pass


class ActionNotFoundError(Exception):
    """
    Error raised when trying to schedule an action that doesn't exist
    """

    pass
