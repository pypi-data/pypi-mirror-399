"""Custom exceptions for the peakfinder package."""


class PeakFinderError(Exception):
    """Base exception for all peakfinder errors."""

    pass


class ValidationError(PeakFinderError):
    """Raised when input validation fails."""

    pass


class AlgorithmError(PeakFinderError):
    """Raised when an algorithm encounters an unexpected error."""

    pass


class DimensionError(PeakFinderError):
    """Raised when an operation is attempted on unsupported dimensions."""

    pass

