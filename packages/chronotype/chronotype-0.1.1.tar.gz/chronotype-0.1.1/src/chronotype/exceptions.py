"""Custom exceptions for chronotype."""


class ChronotypeError(Exception):
    """Base exception for all chronotype errors."""

    pass


class EmptyTemporalError(ChronotypeError):
    """Raised when operating on an empty temporal value."""

    def __init__(self, message: str = "Temporal value has no entries") -> None:
        super().__init__(message)


class InvalidTimestampError(ChronotypeError):
    """Raised when an invalid timestamp is provided."""

    def __init__(self, message: str = "Invalid timestamp provided") -> None:
        super().__init__(message)


class InterpolationError(ChronotypeError):
    """Raised when interpolation fails."""

    def __init__(self, message: str = "Interpolation failed") -> None:
        super().__init__(message)


class ImmutableTemporalError(ChronotypeError):
    """Raised when trying to modify an immutable temporal."""

    def __init__(self, message: str = "Cannot modify immutable temporal") -> None:
        super().__init__(message)