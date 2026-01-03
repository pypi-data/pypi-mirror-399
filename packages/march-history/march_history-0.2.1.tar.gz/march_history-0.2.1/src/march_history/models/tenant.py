from __future__ import annotations

"""Tenant model for march-history SDK."""

from march_history.models.common import TimestampedModel


class Tenant(TimestampedModel):
    """
    Represents a tenant in the conversation history system.

    Tenants provide multi-tenancy support and are automatically created
    when conversations reference them by name.

    Attributes:
        id: Unique tenant identifier
        name: Tenant name (unique)
        created_at: Timestamp when tenant was created
        updated_at: Timestamp when tenant was last updated
    """

    id: int
    name: str
