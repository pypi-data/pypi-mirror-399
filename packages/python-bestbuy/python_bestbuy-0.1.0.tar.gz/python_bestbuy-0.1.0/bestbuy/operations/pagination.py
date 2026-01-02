"""Pagination helpers for Best Buy Catalog API operations."""

from typing import (
    Any,
    AsyncIterator,
    Callable,
    Generic,
    Iterator,
    List,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)


@runtime_checkable
class PaginatedResponse(Protocol):
    """Protocol for paginated API responses."""

    current_page: int
    total_pages: int
    total: int


T = TypeVar("T", bound=PaginatedResponse)
ItemT = TypeVar("ItemT")


class Paginator(Generic[T, ItemT]):
    """Iterator for paginated API responses.

    Allows easy iteration over all pages or all items in a paginated response.

    Example usage:
        # Iterate over pages
        for page in client.products.search_pages(query="onSale=true"):
            print(f"Page {page.current_page} of {page.total_pages}")
            for product in page.products:
                print(product.name)

        # Iterate over all items directly
        for product in client.products.search_pages(query="onSale=true").items():
            print(product.name)

        # Get all items as a list
        all_products = list(client.products.search_pages(query="onSale=true").items())
    """

    def __init__(
        self,
        fetch_page: Callable[[int], T],
        items_attr: str,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> None:
        """Initialize the paginator.

        Args:
            fetch_page: Function that fetches a page given a page number.
            items_attr: Name of the attribute containing items in the response.
            page_size: Number of items per page.
            max_pages: Maximum number of pages to fetch (None for all).
        """
        self._fetch_page = fetch_page
        self._items_attr = items_attr
        self._page_size = page_size
        self._max_pages = max_pages
        self._current_page = 0
        self._total_pages: Optional[int] = None
        self._total: Optional[int] = None

    @property
    def total_pages(self) -> Optional[int]:
        """Total number of pages (available after first fetch)."""
        return self._total_pages

    @property
    def total(self) -> Optional[int]:
        """Total number of items (available after first fetch)."""
        return self._total

    def __iter__(self) -> Iterator[T]:
        """Iterate over pages."""
        self._current_page = 0
        return self

    def __next__(self) -> T:
        """Fetch the next page."""
        next_page = self._current_page + 1

        # Check max_pages limit
        if self._max_pages is not None and next_page > self._max_pages:
            raise StopIteration

        # Check if we've fetched all pages
        if self._total_pages is not None and next_page > self._total_pages:
            raise StopIteration

        response = self._fetch_page(next_page)
        self._current_page = response.current_page
        self._total_pages = response.total_pages
        self._total = response.total

        return response

    def items(self) -> Iterator[ItemT]:
        """Iterate over all items across all pages.

        Yields:
            Individual items from each page.
        """
        for page in self:
            yield from getattr(page, self._items_attr)

    def first(self) -> T:
        """Fetch only the first page.

        Returns:
            The first page of results.
        """
        return self._fetch_page(1)

    def all_items(self) -> List[ItemT]:
        """Fetch all items across all pages.

        Returns:
            List of all items.
        """
        return list(self.items())


class AsyncPaginator(Generic[T, ItemT]):
    """Async iterator for paginated API responses.

    Allows easy async iteration over all pages or all items in a paginated response.

    Example usage:
        # Iterate over pages
        async for page in client.products.search_pages(query="onSale=true"):
            print(f"Page {page.current_page} of {page.total_pages}")
            for product in page.products:
                print(product.name)

        # Iterate over all items directly
        async for product in client.products.search_pages(query="onSale=true").items():
            print(product.name)

        # Get all items as a list
        all_products = await client.products.search_pages(query="onSale=true").all_items()
    """

    def __init__(
        self,
        fetch_page: Callable[[int], Any],  # Returns Awaitable[T]
        items_attr: str,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> None:
        """Initialize the async paginator.

        Args:
            fetch_page: Async function that fetches a page given a page number.
            items_attr: Name of the attribute containing items in the response.
            page_size: Number of items per page.
            max_pages: Maximum number of pages to fetch (None for all).
        """
        self._fetch_page = fetch_page
        self._items_attr = items_attr
        self._page_size = page_size
        self._max_pages = max_pages
        self._current_page = 0
        self._total_pages: Optional[int] = None
        self._total: Optional[int] = None

    @property
    def total_pages(self) -> Optional[int]:
        """Total number of pages (available after first fetch)."""
        return self._total_pages

    @property
    def total(self) -> Optional[int]:
        """Total number of items (available after first fetch)."""
        return self._total

    def __aiter__(self) -> AsyncIterator[T]:
        """Iterate over pages asynchronously."""
        self._current_page = 0
        return self

    async def __anext__(self) -> T:
        """Fetch the next page asynchronously."""
        next_page = self._current_page + 1

        # Check max_pages limit
        if self._max_pages is not None and next_page > self._max_pages:
            raise StopAsyncIteration

        # Check if we've fetched all pages
        if self._total_pages is not None and next_page > self._total_pages:
            raise StopAsyncIteration

        response = await self._fetch_page(next_page)
        self._current_page = response.current_page
        self._total_pages = response.total_pages
        self._total = response.total

        return response

    async def items(self) -> AsyncIterator[ItemT]:
        """Iterate over all items across all pages asynchronously.

        Yields:
            Individual items from each page.
        """
        async for page in self:
            for item in getattr(page, self._items_attr):
                yield item

    async def first(self) -> T:
        """Fetch only the first page asynchronously.

        Returns:
            The first page of results.
        """
        return await self._fetch_page(1)

    async def all_items(self) -> List[ItemT]:
        """Fetch all items across all pages asynchronously.

        Returns:
            List of all items.
        """
        items = []
        async for item in self.items():
            items.append(item)
        return items
