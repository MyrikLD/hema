class NotATrainerError(Exception):
    """Raised when a non-trainer tries to perform a trainer-only action."""

    pass


class AlreadyMarkedError(Exception):
    def __init__(self, username: str):
        self.username = username
