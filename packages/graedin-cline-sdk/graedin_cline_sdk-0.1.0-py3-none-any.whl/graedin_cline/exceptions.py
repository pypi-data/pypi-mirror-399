"""Custom exceptions for Graedin Cline SDK."""


class GraedinError(Exception):
    """Base exception for all Graedin SDK errors."""

    pass


class AuthenticationError(GraedinError):
    """Raised when authentication fails (invalid API key)."""

    pass


class RateLimitError(GraedinError):
    """Raised when rate limit is exceeded."""

    pass


class TimeoutError(GraedinError):
    """Raised when a request times out."""

    pass


class APIError(GraedinError):
    """Raised when the API returns an error response."""

    pass


class ValidationError(GraedinError):
    """Raised when input validation fails."""

    pass
