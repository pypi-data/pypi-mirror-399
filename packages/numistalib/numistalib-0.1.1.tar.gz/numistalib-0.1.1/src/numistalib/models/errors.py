"""Numista error models.

Pydantic models for Numista API error responses.
"""

from pydantic import Field

from numistalib.models.base import NumistaBaseModel


class ErrorResponse(NumistaBaseModel):
    """API error response.

    Maps to Numista error schema from API responses.

    Parameters
    ----------
    error_message : str
        Human-readable error description

    Examples
    --------
    >>> error = ErrorResponse(error_message="Invalid API key")
    >>> print(error.error_message)
    Invalid API key
    """

    error_message: str = Field(description="Error description")
