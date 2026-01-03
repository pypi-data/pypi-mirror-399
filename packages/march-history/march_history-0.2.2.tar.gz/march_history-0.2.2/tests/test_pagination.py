"""Tests for pagination functionality."""

import pytest
import respx
from httpx import Response

from march_history.pagination import AsyncPaginator, Page, SyncPaginator


class TestPage:
    """Test Page model."""

    def test_page_creation(self):
        """Test creating a page."""
        items = [1, 2, 3, 4, 5]
        page = Page(items, offset=0, limit=5)

        assert len(page) == 5
        assert page.offset == 0
        assert page.limit == 5
        assert page.has_more is True  # Full page

    def test_page_iteration(self):
        """Test iterating over page items."""
        items = [1, 2, 3]
        page = Page(items, offset=0, limit=5)

        result = list(page)
        assert result == [1, 2, 3]

    def test_page_has_more_full_page(self):
        """Test has_more is True when page is full."""
        items = list(range(10))
        page = Page(items, offset=0, limit=10)

        assert page.has_more is True

    def test_page_has_more_partial_page(self):
        """Test has_more is False when page is partial."""
        items = [1, 2, 3]
        page = Page(items, offset=0, limit=10)

        assert page.has_more is False


class TestSyncPaginator:
    """Test SyncPaginator."""

    def test_basic_pagination(self):
        """Test basic pagination over multiple pages."""
        # Mock fetch function
        pages = [
            [1, 2, 3],  # Page 1
            [4, 5, 6],  # Page 2
            [7, 8],     # Page 3 (partial)
        ]
        page_index = [0]

        def fetch_page(offset: int, limit: int) -> list[int]:
            if page_index[0] >= len(pages):
                return []
            result = pages[page_index[0]]
            page_index[0] += 1
            return result

        paginator = SyncPaginator(fetch_page, page_size=3)
        items = list(paginator)

        assert items == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_pagination_with_max_items(self):
        """Test pagination stops at max_items."""
        def fetch_page(offset: int, limit: int) -> list[int]:
            # Return unlimited items
            return list(range(offset, offset + limit))

        paginator = SyncPaginator(fetch_page, page_size=5, max_items=12)
        items = list(paginator)

        assert len(items) == 12

    def test_pagination_empty_first_page(self):
        """Test pagination when first page is empty."""
        def fetch_page(offset: int, limit: int) -> list[int]:
            return []

        paginator = SyncPaginator(fetch_page, page_size=10)
        items = list(paginator)

        assert items == []

    def test_pagination_pages_iterator(self):
        """Test iterating over pages."""
        pages_data = [
            [1, 2, 3],
            [4, 5, 6],
            [7],
        ]
        page_index = [0]

        def fetch_page(offset: int, limit: int) -> list[int]:
            if page_index[0] >= len(pages_data):
                return []
            result = pages_data[page_index[0]]
            page_index[0] += 1
            return result

        paginator = SyncPaginator(fetch_page, page_size=3)
        pages = list(paginator.pages())

        assert len(pages) == 3
        assert len(pages[0].items) == 3
        assert len(pages[1].items) == 3
        assert len(pages[2].items) == 1
        assert pages[2].has_more is False


class TestPaginationIntegration:
    """Test pagination with actual API calls."""

    @respx.mock
    def test_list_iter_single_page(self, client, base_url, tenant_response):
        """Test list_iter with single page of results."""
        respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(200, json=[tenant_response])
        )

        tenants = list(client.tenants.list_iter(page_size=10))

        assert len(tenants) == 1
        assert tenants[0].id == 1

    @respx.mock
    def test_list_iter_multiple_pages(self, client, base_url, tenant_response):
        """Test list_iter with multiple pages."""
        # First page: 2 items
        # Second page: 1 item (partial page, should stop)
        responses = {
            0: [
                {**tenant_response, "id": 1, "name": "tenant-1"},
                {**tenant_response, "id": 2, "name": "tenant-2"},
            ],
            2: [
                {**tenant_response, "id": 3, "name": "tenant-3"},
            ],
        }

        def handle_request(request):
            offset = int(request.url.params.get("offset", 0))
            return Response(200, json=responses.get(offset, []))

        respx.get(f"{base_url}/tenants/").mock(side_effect=handle_request)

        tenants = list(client.tenants.list_iter(page_size=2))

        assert len(tenants) == 3
        assert tenants[0].name == "tenant-1"
        assert tenants[1].name == "tenant-2"
        assert tenants[2].name == "tenant-3"

    @respx.mock
    def test_list_iter_with_max_items(self, client, base_url, conversation_response):
        """Test list_iter respects max_items limit."""
        # Return 10 items but only fetch first 5
        items = [
            {**conversation_response, "id": i, "title": f"Conv {i}"}
            for i in range(1, 11)
        ]

        respx.get(f"{base_url}/conversations/").mock(
            return_value=Response(200, json=items)
        )

        conversations = list(client.conversations.list_iter(
            page_size=10,
            max_items=5
        ))

        assert len(conversations) == 5

    @respx.mock
    def test_search_iter(self, client, base_url, conversation_response):
        """Test search with pagination."""
        def handle_request(request):
            offset = int(request.url.params.get("offset", 0))
            if offset >= 3:
                return Response(200, json=[])
            return Response(200, json=[
                {**conversation_response, "id": offset + 1}
            ])

        respx.get(f"{base_url}/conversations/search").mock(
            side_effect=handle_request
        )

        results = list(client.conversations.search_iter(
            q="test",
            page_size=1
        ))

        assert len(results) == 3


class TestAsyncPaginator:
    """Test AsyncPaginator."""

    @pytest.mark.asyncio
    async def test_basic_async_pagination(self):
        """Test basic async pagination over multiple pages."""
        pages = [
            [1, 2, 3],  # Page 1
            [4, 5, 6],  # Page 2
            [7, 8],     # Page 3 (partial)
        ]
        page_index = [0]

        async def fetch_page(offset: int, limit: int) -> list[int]:
            if page_index[0] >= len(pages):
                return []
            result = pages[page_index[0]]
            page_index[0] += 1
            return result

        paginator = AsyncPaginator(fetch_page, page_size=3)
        items = [item async for item in paginator]

        assert items == [1, 2, 3, 4, 5, 6, 7, 8]

    @pytest.mark.asyncio
    async def test_async_pagination_with_max_items(self):
        """Test async pagination stops at max_items."""
        async def fetch_page(offset: int, limit: int) -> list[int]:
            return list(range(offset, offset + limit))

        paginator = AsyncPaginator(fetch_page, page_size=5, max_items=12)
        items = [item async for item in paginator]

        assert len(items) == 12

    @pytest.mark.asyncio
    async def test_async_pagination_empty_first_page(self):
        """Test async pagination when first page is empty."""
        async def fetch_page(offset: int, limit: int) -> list[int]:
            return []

        paginator = AsyncPaginator(fetch_page, page_size=10)
        items = [item async for item in paginator]

        assert items == []

    @pytest.mark.asyncio
    async def test_async_pagination_pages_iterator(self):
        """Test iterating over async pages."""
        pages_data = [
            [1, 2, 3],
            [4, 5, 6],
            [7],
        ]
        page_index = [0]

        async def fetch_page(offset: int, limit: int) -> list[int]:
            if page_index[0] >= len(pages_data):
                return []
            result = pages_data[page_index[0]]
            page_index[0] += 1
            return result

        paginator = AsyncPaginator(fetch_page, page_size=3)
        pages = [page async for page in paginator.pages()]

        assert len(pages) == 3
        assert len(pages[0].items) == 3
        assert len(pages[1].items) == 3
        assert len(pages[2].items) == 1
        assert pages[2].has_more is False


class TestAsyncPaginationIntegration:
    """Test async pagination with actual API calls."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_iter_single_page(
        self, async_client, base_url, tenant_response
    ):
        """Test async list_iter with single page of results."""
        respx.get(f"{base_url}/tenants/").mock(
            return_value=Response(200, json=[tenant_response])
        )

        tenants = [t async for t in async_client.tenants.list_iter(page_size=10)]

        assert len(tenants) == 1
        assert tenants[0].id == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_iter_multiple_pages(
        self, async_client, base_url, tenant_response
    ):
        """Test async list_iter with multiple pages."""
        responses = {
            0: [
                {**tenant_response, "id": 1, "name": "tenant-1"},
                {**tenant_response, "id": 2, "name": "tenant-2"},
            ],
            2: [
                {**tenant_response, "id": 3, "name": "tenant-3"},
            ],
        }

        def handle_request(request):
            offset = int(request.url.params.get("offset", 0))
            return Response(200, json=responses.get(offset, []))

        respx.get(f"{base_url}/tenants/").mock(side_effect=handle_request)

        tenants = [t async for t in async_client.tenants.list_iter(page_size=2)]

        assert len(tenants) == 3
        assert tenants[0].name == "tenant-1"
        assert tenants[1].name == "tenant-2"
        assert tenants[2].name == "tenant-3"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_iter_with_max_items(
        self, async_client, base_url, conversation_response
    ):
        """Test async list_iter respects max_items limit."""
        items = [
            {**conversation_response, "id": i, "title": f"Conv {i}"}
            for i in range(1, 11)
        ]

        respx.get(f"{base_url}/conversations/").mock(
            return_value=Response(200, json=items)
        )

        conversations = [
            c async for c in async_client.conversations.list_iter(
                page_size=10,
                max_items=5
            )
        ]

        assert len(conversations) == 5

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_search_iter(
        self, async_client, base_url, conversation_response
    ):
        """Test async search with pagination."""
        def handle_request(request):
            offset = int(request.url.params.get("offset", 0))
            if offset >= 3:
                return Response(200, json=[])
            return Response(200, json=[
                {**conversation_response, "id": offset + 1}
            ])

        respx.get(f"{base_url}/conversations/search").mock(
            side_effect=handle_request
        )

        results = [
            r async for r in async_client.conversations.search_iter(
                q="test",
                page_size=1
            )
        ]

        assert len(results) == 3
