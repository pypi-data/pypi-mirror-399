"""Numista users models.

Pydantic models for Numista user profiles.
"""

from pydantic import Field, HttpUrl, computed_field

from numistalib.models.base import NumistaBaseModel


class User(NumistaBaseModel):
    """Numista user profile information.

    Maps to Numista user entity.

    Parameters
    ----------
    numista_id : int
        Numista user ID
    username : str
        Unique username
    avatar : HttpUrl | None
        URL to avatar picture (optional)
    country_code : str | None
        ISO country code (optional, not in swagger)
    member_since : str | None
        Registration date (optional, not in swagger)
    """

    numista_id: int = Field(alias="id", gt=0, description="Numista user ID")
    username: str = Field(max_length=100, description="Unique username")
    avatar: HttpUrl | None = Field(None, description="URL to avatar picture")
    country_code: str | None = Field(None, max_length=10, description="ISO country code")
    member_since: str | None = Field(None, description="Registration date")

    @computed_field(description="User profile display")
    def user_profile(self) -> str:
        """Formatted user profile."""
        country = f" ({self.country_code})" if self.country_code else ""
        return f"{self.username}{country}"

    def to_dict(self) -> dict[str, object]:
        """Convert user to dictionary representation."""
        return self.model_dump(exclude_none=True)
