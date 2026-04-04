class PriceMindError(Exception):
    """Base project exception."""


class ValidationError(PriceMindError):
    """Raised when a validation rule fails."""
