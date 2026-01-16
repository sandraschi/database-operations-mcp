"""Firefox-specific exceptions."""


class FirefoxNotClosedError(Exception):
    """Raised when Firefox is running and database access would be unsafe."""

    pass

