from __future__ import annotations

"""Tenant resource for march-history SDK."""

from collections.abc import Iterator

from march_history.models.tenant import Tenant
from march_history.pagination import SyncPaginator
from march_history.resources._base import BaseResource


class TenantResource(BaseResource):
    """
    Tenant management resource.

    Provides read-only access to tenant information. Tenants are automatically
    created when conversations reference them by name.
    """

    def list(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Tenant]:
        """
        Retrieve a paginated list of all tenants.

        Args:
            offset: Number of items to skip (default: 0)
            limit: Number of items to return (default: 100, max: 1000)

        Returns:
            List of tenants

        Example:
            >>> tenants = client.tenants.list(offset=0, limit=50)
            >>> for tenant in tenants:
            ...     print(tenant.name)
        """
        params = {"offset": offset, "limit": limit}
        data = self._get("/tenants/", params=params)
        return [Tenant(**item) for item in data]

    def list_iter(
        self,
        page_size: int = 100,
        max_items: int | None = None,
    ) -> Iterator[Tenant]:
        """
        Iterate over all tenants with auto-pagination.

        Args:
            page_size: Number of items per page (default: 100)
            max_items: Maximum total items to fetch (default: unlimited)

        Returns:
            Iterator yielding tenants

        Example:
            >>> for tenant in client.tenants.list_iter():
            ...     print(tenant.name)
        """

        def fetch_page(offset: int, limit: int) -> list[Tenant]:
            return self.list(offset=offset, limit=limit)

        return SyncPaginator(fetch_page, page_size, max_items)

    def get(self, tenant_id: int) -> Tenant:
        """
        Retrieve a specific tenant by ID.

        Args:
            tenant_id: Tenant ID

        Returns:
            Tenant object

        Raises:
            NotFoundError: If tenant not found
            ValidationError: If tenant_id is invalid

        Example:
            >>> tenant = client.tenants.get(1)
            >>> print(tenant.name)
        """
        data = self._get(f"/tenants/{tenant_id}")
        return Tenant(**data)

    def get_by_name(self, tenant_name: str) -> Tenant:
        """
        Retrieve a specific tenant by name.

        Args:
            tenant_name: Tenant name

        Returns:
            Tenant object

        Raises:
            NotFoundError: If tenant not found

        Example:
            >>> tenant = client.tenants.get_by_name("acme-corp")
            >>> print(tenant.id)
        """
        data = self._get(f"/tenants/by-name/{tenant_name}")
        return Tenant(**data)
