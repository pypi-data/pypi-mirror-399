from __future__ import annotations

"""Async tenant resource for march-history SDK."""

from collections.abc import AsyncIterator

from march_history._async.resources._base import AsyncBaseResource
from march_history.models.tenant import Tenant
from march_history.pagination import AsyncPaginator


class AsyncTenantResource(AsyncBaseResource):
    """
    Async tenant management resource.

    Provides read-only access to tenant information. Tenants are automatically
    created when conversations reference them by name.
    """

    async def list(
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
            >>> tenants = await client.tenants.list(offset=0, limit=50)
            >>> for tenant in tenants:
            ...     print(tenant.name)
        """
        params = {"offset": offset, "limit": limit}
        data = await self._get("/tenants/", params=params)
        return [Tenant(**item) for item in data]

    def list_iter(
        self,
        page_size: int = 100,
        max_items: int | None = None,
    ) -> AsyncIterator[Tenant]:
        """
        Iterate over all tenants with auto-pagination.

        Args:
            page_size: Number of items per page (default: 100)
            max_items: Maximum total items to fetch (default: unlimited)

        Returns:
            AsyncIterator yielding tenants

        Example:
            >>> async for tenant in client.tenants.list_iter():
            ...     print(tenant.name)
        """

        async def fetch_page(offset: int, limit: int) -> list[Tenant]:
            return await self.list(offset=offset, limit=limit)

        return AsyncPaginator(fetch_page, page_size, max_items)

    async def get(self, tenant_id: int) -> Tenant:
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
            >>> tenant = await client.tenants.get(1)
            >>> print(tenant.name)
        """
        data = await self._get(f"/tenants/{tenant_id}")
        return Tenant(**data)

    async def get_by_name(self, tenant_name: str) -> Tenant:
        """
        Retrieve a specific tenant by name.

        Args:
            tenant_name: Tenant name

        Returns:
            Tenant object

        Raises:
            NotFoundError: If tenant not found

        Example:
            >>> tenant = await client.tenants.get_by_name("acme-corp")
            >>> print(tenant.id)
        """
        data = await self._get(f"/tenants/by-name/{tenant_name}")
        return Tenant(**data)
