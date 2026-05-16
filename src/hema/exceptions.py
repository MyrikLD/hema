class NotATrainerError(Exception):
    """Raised when a non-trainer tries to perform a trainer-only action."""

    pass
