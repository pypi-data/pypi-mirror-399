from __future__ import annotations

"""Pagination helpers for march-history SDK."""

from collections.abc import AsyncIterator, Awaitable, Iterator
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class Page(Generic[T]):
    """
    Represents a single page of results.

    Attributes:
        items: List of items in this page
        offset: Starting offset for this page
        limit: Maximum number of items per page
        total: Total number of items (if available)
        has_more: Whether there are more pages available (heuristic)
    """

    def __init__(
        self,
        items: list[T],
        offset: int,
        limit: int,
        total: int | None = None,
    ) -> None:
        """
        Initialize page.

        Args:
            items: List of items in this page
            offset: Starting offset
            limit: Page size limit
            total: Total count (if known)
        """
        self.items = items
        self.offset = offset
        self.limit = limit
        self.total = total
        # Heuristic: If we got a full page, there might be more
        self.has_more = len(items) == limit

    def __iter__(self) -> Iterator[T]:
        """Iterate over items in this page."""
        return iter(self.items)

    def __len__(self) -> int:
        """Get number of items in this page."""
        return len(self.items)


class SyncPaginator(Generic[T]):
    """
    Iterator for paginated API results (sync version).

    Automatically fetches pages as needed while iterating.

    Example:
        >>> for item in paginator:
        ...     print(item)

        >>> for page in paginator.pages():
        ...     print(f"Page with {len(page)} items")
    """

    def __init__(
        self,
        fetch_page: Callable[[int, int], list[T]],
        page_size: int = 100,
        max_items: int | None = None,
    ) -> None:
        """
        Initialize paginator.

        Args:
            fetch_page: Function to fetch a page (offset, limit) -> list[T]
            page_size: Number of items per page
            max_items: Maximum total items to fetch (None for unlimited)
        """
        self._fetch_page = fetch_page
        self._page_size = page_size
        self._max_items = max_items
        self._offset = 0
        self._total_fetched = 0

    def __iter__(self) -> Iterator[T]:
        """Iterate over all items across all pages."""
        while True:
            # Check if we've reached max_items
            if self._max_items and self._total_fetched >= self._max_items:
                break

            # Fetch next page
            items = self._fetch_page(self._offset, self._page_size)
            if not items:
                break

            # Yield items
            for item in items:
                if self._max_items and self._total_fetched >= self._max_items:
                    return
                yield item
                self._total_fetched += 1

            # Move to next page
            self._offset += len(items)

            # If we got fewer items than page_size, we're done
            if len(items) < self._page_size:
                break

    def pages(self) -> Iterator[Page[T]]:
        """
        Iterate over pages instead of individual items.

        Yields:
            Page objects containing items
        """
        offset = 0
        total_fetched = 0

        while True:
            if self._max_items and total_fetched >= self._max_items:
                break

            items = self._fetch_page(offset, self._page_size)
            if not items:
                break

            page = Page(items, offset, self._page_size)
            yield page

            total_fetched += len(items)
            offset += len(items)

            if not page.has_more:
                break


class AsyncPaginator(Generic[T]):
    """
    Async iterator for paginated API results.

    Automatically fetches pages as needed while iterating.

    Example:
        >>> async for item in paginator:
        ...     print(item)

        >>> async for page in paginator.pages():
        ...     print(f"Page with {len(page)} items")
    """

    def __init__(
        self,
        fetch_page: Callable[[int, int], Awaitable[list[T]]],
        page_size: int = 100,
        max_items: int | None = None,
    ) -> None:
        """
        Initialize async paginator.

        Args:
            fetch_page: Async function to fetch a page (offset, limit) -> list[T]
            page_size: Number of items per page
            max_items: Maximum total items to fetch (None for unlimited)
        """
        self._fetch_page = fetch_page
        self._page_size = page_size
        self._max_items = max_items
        self._offset = 0
        self._total_fetched = 0

    async def __aiter__(self) -> AsyncIterator[T]:
        """Async iterate over all items across all pages."""
        while True:
            # Check if we've reached max_items
            if self._max_items and self._total_fetched >= self._max_items:
                break

            # Fetch next page
            items = await self._fetch_page(self._offset, self._page_size)
            if not items:
                break

            # Yield items
            for item in items:
                if self._max_items and self._total_fetched >= self._max_items:
                    return
                yield item
                self._total_fetched += 1

            # Move to next page
            self._offset += len(items)

            # If we got fewer items than page_size, we're done
            if len(items) < self._page_size:
                break

    async def pages(self) -> AsyncIterator[Page[T]]:
        """
        Async iterate over pages instead of individual items.

        Yields:
            Page objects containing items
        """
        offset = 0
        total_fetched = 0

        while True:
            if self._max_items and total_fetched >= self._max_items:
                break

            items = await self._fetch_page(offset, self._page_size)
            if not items:
                break

            page = Page(items, offset, self._page_size)
            yield page

            total_fetched += len(items)
            offset += len(items)

            if not page.has_more:
                break
