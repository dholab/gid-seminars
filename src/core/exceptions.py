# GID Seminars - Custom Exceptions
"""Custom exception classes for error handling."""


class GIDSeminarsError(Exception):
    """Base exception for GID Seminars."""

    pass


class SourceError(GIDSeminarsError):
    """Error fetching from a source."""

    def __init__(
        self, source_id: str, message: str, original_error: Exception | None = None
    ):
        self.source_id = source_id
        self.original_error = original_error
        super().__init__(f"[{source_id}] {message}")


class ParseError(SourceError):
    """Error parsing source data."""

    pass


class NetworkError(SourceError):
    """Network-related error."""

    pass


class DatabaseError(GIDSeminarsError):
    """Database operation error."""

    pass


class ConfigurationError(GIDSeminarsError):
    """Configuration validation error."""

    pass


class DeploymentError(GIDSeminarsError):
    """Error deploying to target."""

    pass
