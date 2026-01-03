from __future__ import annotations

"""Common Pydantic models for march-history SDK."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseAPIModel(BaseModel):
    """
    Base model for all API models.

    Provides common configuration for Pydantic models used in the SDK.
    """

    model_config = ConfigDict(
        frozen=False,  # Allow mutation
        extra="forbid",  # Reject extra fields not defined in model
        use_enum_values=True,  # Use enum values instead of enum objects
        populate_by_name=True,  # Allow population by field name or alias
    )


class TimestampedModel(BaseAPIModel):
    """
    Base model for API models with timestamp fields.

    Attributes:
        created_at: Timestamp when the resource was created
        updated_at: Timestamp when the resource was last updated
    """

    created_at: datetime
    updated_at: datetime
