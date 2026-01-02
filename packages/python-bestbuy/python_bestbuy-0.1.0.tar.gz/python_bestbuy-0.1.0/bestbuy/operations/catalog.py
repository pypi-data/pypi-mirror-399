"""Catalog API operations for Best Buy."""

from typing import List, Optional

from .base import BaseOperations
from .pagination import AsyncPaginator, Paginator
from ..models import (
    CatalogStore,
    CatalogStoresResponse,
    CategoriesResponse,
    Category,
    Product,
    ProductsResponse,
    RecommendationsResponse,
)


class ProductOperations(BaseOperations):
    """Operations for the Products API."""

    def get(
        self,
        sku: int | str,
        show: Optional[List[str]] = None,
    ) -> Product:
        """Get a single product by SKU.

        Args:
            sku: The Best Buy product SKU.
            show: Optional list of attributes to return. If None, returns all.

        Returns:
            The product details.
        """
        params = {"apiKey": self.client.options.api_key}
        if show:
            params["show"] = ",".join(show)
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/products/{sku}.json",
            params=params,
        )
        response = self.client.request(request)
        return Product.model_validate(response.json())

    def search(
        self,
        query: Optional[str] = None,
        show: Optional[List[str]] = None,
        sort: Optional[str] = None,
        sort_order: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        facet: Optional[str] = None,
        cursor_mark: Optional[str] = None,
    ) -> ProductsResponse:
        """Search for products.

        Args:
            query: Search query string (e.g., "manufacturer=canon&salePrice<1000").
            show: Optional list of attributes to return.
            sort: Attribute to sort by.
            sort_order: Sort direction ("asc" or "desc").
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).
            facet: Facet attribute and count (e.g., "manufacturer,5").
            cursor_mark: Cursor mark for deep pagination.

        Returns:
            ProductsResponse containing matching products.
        """
        params = {
            "apiKey": self.client.options.api_key,
            "page": page,
            "pageSize": page_size,
        }
        if show:
            params["show"] = ",".join(show)
        if sort:
            sort_str = sort
            if sort_order:
                sort_str = f"{sort}.{sort_order}"
            params["sort"] = sort_str
        if facet:
            params["facet"] = facet
        if cursor_mark:
            params["cursorMark"] = cursor_mark
        # Build URL with query in path (Best Buy API v1 style)
        url = "/v1/products.json"
        if query:
            url = f"/v1/products({query}).json"
        request = self.client.client.build_request(
            method="GET",
            url=url,
            params=params,
        )
        response = self.client.request(request)
        return ProductsResponse.model_validate(response.json())

    def list(
        self,
        show: Optional[List[str]] = None,
        sort: Optional[str] = None,
        sort_order: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> ProductsResponse:
        """List all products.

        Args:
            show: Optional list of attributes to return.
            sort: Attribute to sort by.
            sort_order: Sort direction ("asc" or "desc").
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).

        Returns:
            ProductsResponse containing products.
        """
        return self.search(
            query=None,
            show=show,
            sort=sort,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )

    def get_warranties(
        self,
        sku: int | str,
    ) -> List[dict]:
        """Get warranties for a product.

        Args:
            sku: The Best Buy product SKU.

        Returns:
            List of warranty information dictionaries.
        """
        params = {"apiKey": self.client.options.api_key}
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/products/{sku}/warranties.json",
            params=params,
        )
        response = self.client.request(request)
        return response.json()

    def search_pages(
        self,
        query: Optional[str] = None,
        show: Optional[List[str]] = None,
        sort: Optional[str] = None,
        sort_order: Optional[str] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> Paginator[ProductsResponse, Product]:
        """Search for products with automatic pagination.

        Returns a Paginator that can iterate over all pages or items.

        Args:
            query: Search query string (e.g., "manufacturer=canon&salePrice<1000").
            show: Optional list of attributes to return.
            sort: Attribute to sort by.
            sort_order: Sort direction ("asc" or "desc").
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            Paginator for iterating over pages or products.

        Example:
            # Iterate over pages
            for page in client.products.search_pages(query="onSale=true"):
                for product in page.products:
                    print(product.name)

            # Iterate over all products directly
            for product in client.products.search_pages(query="onSale=true").items():
                print(product.name)
        """

        def fetch_page(page: int) -> ProductsResponse:
            return self.search(
                query=query,
                show=show,
                sort=sort,
                sort_order=sort_order,
                page=page,
                page_size=page_size,
            )

        return Paginator(
            fetch_page=fetch_page,
            items_attr="products",
            page_size=page_size,
            max_pages=max_pages,
        )

    def list_pages(
        self,
        show: Optional[List[str]] = None,
        sort: Optional[str] = None,
        sort_order: Optional[str] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> Paginator[ProductsResponse, Product]:
        """List all products with automatic pagination.

        Returns a Paginator that can iterate over all pages or items.

        Args:
            show: Optional list of attributes to return.
            sort: Attribute to sort by.
            sort_order: Sort direction ("asc" or "desc").
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            Paginator for iterating over pages or products.
        """
        return self.search_pages(
            query=None,
            show=show,
            sort=sort,
            sort_order=sort_order,
            page_size=page_size,
            max_pages=max_pages,
        )


class AsyncProductOperations(BaseOperations):
    """Async operations for the Products API."""

    async def get(
        self,
        sku: int | str,
        show: Optional[List[str]] = None,
    ) -> Product:
        """Get a single product by SKU.

        Args:
            sku: The Best Buy product SKU.
            show: Optional list of attributes to return. If None, returns all.

        Returns:
            The product details.
        """
        params = {"apiKey": self.client.options.api_key}
        if show:
            params["show"] = ",".join(show)
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/products/{sku}.json",
            params=params,
        )
        response = await self.client.request(request)
        return Product.model_validate(response.json())

    async def search(
        self,
        query: Optional[str] = None,
        show: Optional[List[str]] = None,
        sort: Optional[str] = None,
        sort_order: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        facet: Optional[str] = None,
        cursor_mark: Optional[str] = None,
    ) -> ProductsResponse:
        """Search for products.

        Args:
            query: Search query string (e.g., "manufacturer=canon&salePrice<1000").
            show: Optional list of attributes to return.
            sort: Attribute to sort by.
            sort_order: Sort direction ("asc" or "desc").
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).
            facet: Facet attribute and count (e.g., "manufacturer,5").
            cursor_mark: Cursor mark for deep pagination.

        Returns:
            ProductsResponse containing matching products.
        """
        params = {
            "apiKey": self.client.options.api_key,
            "page": page,
            "pageSize": page_size,
        }
        if show:
            params["show"] = ",".join(show)
        if sort:
            sort_str = sort
            if sort_order:
                sort_str = f"{sort}.{sort_order}"
            params["sort"] = sort_str
        if facet:
            params["facet"] = facet
        if cursor_mark:
            params["cursorMark"] = cursor_mark
        # Build URL with query in path (Best Buy API v1 style)
        url = "/v1/products.json"
        if query:
            url = f"/v1/products({query}).json"
        request = self.client.client.build_request(
            method="GET",
            url=url,
            params=params,
        )
        response = await self.client.request(request)
        return ProductsResponse.model_validate(response.json())

    async def list(
        self,
        show: Optional[List[str]] = None,
        sort: Optional[str] = None,
        sort_order: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> ProductsResponse:
        """List all products.

        Args:
            show: Optional list of attributes to return.
            sort: Attribute to sort by.
            sort_order: Sort direction ("asc" or "desc").
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).

        Returns:
            ProductsResponse containing products.
        """
        return await self.search(
            query=None,
            show=show,
            sort=sort,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )

    async def get_warranties(
        self,
        sku: int | str,
    ) -> List[dict]:
        """Get warranties for a product.

        Args:
            sku: The Best Buy product SKU.

        Returns:
            List of warranty information dictionaries.
        """
        params = {"apiKey": self.client.options.api_key}
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/products/{sku}/warranties.json",
            params=params,
        )
        response = await self.client.request(request)
        return response.json()

    def search_pages(
        self,
        query: Optional[str] = None,
        show: Optional[List[str]] = None,
        sort: Optional[str] = None,
        sort_order: Optional[str] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> AsyncPaginator[ProductsResponse, Product]:
        """Search for products with automatic pagination.

        Returns an AsyncPaginator that can iterate over all pages or items.

        Args:
            query: Search query string (e.g., "manufacturer=canon&salePrice<1000").
            show: Optional list of attributes to return.
            sort: Attribute to sort by.
            sort_order: Sort direction ("asc" or "desc").
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            AsyncPaginator for iterating over pages or products.

        Example:
            # Iterate over pages
            async for page in client.products.search_pages(query="onSale=true"):
                for product in page.products:
                    print(product.name)

            # Iterate over all products directly
            async for product in client.products.search_pages(query="onSale=true").items():
                print(product.name)
        """

        async def fetch_page(page: int) -> ProductsResponse:
            return await self.search(
                query=query,
                show=show,
                sort=sort,
                sort_order=sort_order,
                page=page,
                page_size=page_size,
            )

        return AsyncPaginator(
            fetch_page=fetch_page,
            items_attr="products",
            page_size=page_size,
            max_pages=max_pages,
        )

    def list_pages(
        self,
        show: Optional[List[str]] = None,
        sort: Optional[str] = None,
        sort_order: Optional[str] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> AsyncPaginator[ProductsResponse, Product]:
        """List all products with automatic pagination.

        Returns an AsyncPaginator that can iterate over all pages or items.

        Args:
            show: Optional list of attributes to return.
            sort: Attribute to sort by.
            sort_order: Sort direction ("asc" or "desc").
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            AsyncPaginator for iterating over pages or products.
        """
        return self.search_pages(
            query=None,
            show=show,
            sort=sort,
            sort_order=sort_order,
            page_size=page_size,
            max_pages=max_pages,
        )


class CategoryOperations(BaseOperations):
    """Operations for the Categories API."""

    def get(
        self,
        category_id: str,
        show: Optional[List[str]] = None,
    ) -> Category:
        """Get a single category by ID.

        Args:
            category_id: The category ID.
            show: Optional list of attributes to return.

        Returns:
            The category details.
        """
        params = {"apiKey": self.client.options.api_key}
        if show:
            params["show"] = ",".join(show)
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/categories/{category_id}.json",
            params=params,
        )
        response = self.client.request(request)
        return Category.model_validate(response.json())

    def search(
        self,
        query: Optional[str] = None,
        show: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> CategoriesResponse:
        """Search for categories.

        Args:
            query: Search query string.
            show: Optional list of attributes to return.
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).

        Returns:
            CategoriesResponse containing matching categories.
        """
        params = {
            "apiKey": self.client.options.api_key,
            "page": page,
            "pageSize": page_size,
        }
        if show:
            params["show"] = ",".join(show)
        url = "/v1/categories.json"
        if query:
            url = f"/v1/categories({query}).json"
        request = self.client.client.build_request(
            method="GET",
            url=url,
            params=params,
        )
        response = self.client.request(request)
        return CategoriesResponse.model_validate(response.json())

    def list(
        self,
        show: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> CategoriesResponse:
        """List all categories.

        Args:
            show: Optional list of attributes to return.
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).

        Returns:
            CategoriesResponse containing categories.
        """
        return self.search(
            query=None,
            show=show,
            page=page,
            page_size=page_size,
        )

    def search_pages(
        self,
        query: Optional[str] = None,
        show: Optional[List[str]] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> Paginator[CategoriesResponse, Category]:
        """Search for categories with automatic pagination.

        Args:
            query: Search query string.
            show: Optional list of attributes to return.
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            Paginator for iterating over pages or categories.
        """

        def fetch_page(page: int) -> CategoriesResponse:
            return self.search(
                query=query,
                show=show,
                page=page,
                page_size=page_size,
            )

        return Paginator(
            fetch_page=fetch_page,
            items_attr="categories",
            page_size=page_size,
            max_pages=max_pages,
        )

    def list_pages(
        self,
        show: Optional[List[str]] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> Paginator[CategoriesResponse, Category]:
        """List all categories with automatic pagination.

        Args:
            show: Optional list of attributes to return.
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            Paginator for iterating over pages or categories.
        """
        return self.search_pages(
            query=None,
            show=show,
            page_size=page_size,
            max_pages=max_pages,
        )


class AsyncCategoryOperations(BaseOperations):
    """Async operations for the Categories API."""

    async def get(
        self,
        category_id: str,
        show: Optional[List[str]] = None,
    ) -> Category:
        """Get a single category by ID.

        Args:
            category_id: The category ID.
            show: Optional list of attributes to return.

        Returns:
            The category details.
        """
        params = {"apiKey": self.client.options.api_key}
        if show:
            params["show"] = ",".join(show)
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/categories/{category_id}.json",
            params=params,
        )
        response = await self.client.request(request)
        return Category.model_validate(response.json())

    async def search(
        self,
        query: Optional[str] = None,
        show: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> CategoriesResponse:
        """Search for categories.

        Args:
            query: Search query string.
            show: Optional list of attributes to return.
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).

        Returns:
            CategoriesResponse containing matching categories.
        """
        params = {
            "apiKey": self.client.options.api_key,
            "page": page,
            "pageSize": page_size,
        }
        if show:
            params["show"] = ",".join(show)
        url = "/v1/categories.json"
        if query:
            url = f"/v1/categories({query}).json"
        request = self.client.client.build_request(
            method="GET",
            url=url,
            params=params,
        )
        response = await self.client.request(request)
        return CategoriesResponse.model_validate(response.json())

    async def list(
        self,
        show: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> CategoriesResponse:
        """List all categories.

        Args:
            show: Optional list of attributes to return.
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).

        Returns:
            CategoriesResponse containing categories.
        """
        return await self.search(
            query=None,
            show=show,
            page=page,
            page_size=page_size,
        )

    def search_pages(
        self,
        query: Optional[str] = None,
        show: Optional[List[str]] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> AsyncPaginator[CategoriesResponse, Category]:
        """Search for categories with automatic pagination.

        Args:
            query: Search query string.
            show: Optional list of attributes to return.
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            AsyncPaginator for iterating over pages or categories.
        """

        async def fetch_page(page: int) -> CategoriesResponse:
            return await self.search(
                query=query,
                show=show,
                page=page,
                page_size=page_size,
            )

        return AsyncPaginator(
            fetch_page=fetch_page,
            items_attr="categories",
            page_size=page_size,
            max_pages=max_pages,
        )

    def list_pages(
        self,
        show: Optional[List[str]] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> AsyncPaginator[CategoriesResponse, Category]:
        """List all categories with automatic pagination.

        Args:
            show: Optional list of attributes to return.
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            AsyncPaginator for iterating over pages or categories.
        """
        return self.search_pages(
            query=None,
            show=show,
            page_size=page_size,
            max_pages=max_pages,
        )


class RecommendationOperations(BaseOperations):
    """Operations for the Recommendations API."""

    def trending(
        self,
        category_id: Optional[str] = None,
    ) -> RecommendationsResponse:
        """Get trending products.

        Returns top ten products based on customer views over a rolling
        three hour time period.

        Args:
            category_id: Optional category ID to filter by.

        Returns:
            RecommendationsResponse containing trending products.
        """
        params = {"apiKey": self.client.options.api_key}
        if category_id:
            url = f"/v1/products/trendingViewed(categoryId={category_id}).json"
        else:
            url = "/v1/products/trendingViewed.json"
        request = self.client.client.build_request(
            method="GET",
            url=url,
            params=params,
        )
        response = self.client.request(request)
        return RecommendationsResponse.model_validate(response.json())

    def most_viewed(
        self,
        category_id: Optional[str] = None,
    ) -> RecommendationsResponse:
        """Get most viewed products.

        Returns top ten most frequently viewed products on BESTBUY.COM.

        Args:
            category_id: Optional category ID to filter by.

        Returns:
            RecommendationsResponse containing most viewed products.
        """
        params = {"apiKey": self.client.options.api_key}
        if category_id:
            url = f"/v1/products/mostViewed(categoryId={category_id}).json"
        else:
            url = "/v1/products/mostViewed.json"
        request = self.client.client.build_request(
            method="GET",
            url=url,
            params=params,
        )
        response = self.client.request(request)
        return RecommendationsResponse.model_validate(response.json())

    def also_viewed(
        self,
        sku: int | str,
    ) -> RecommendationsResponse:
        """Get products also viewed with the specified product.

        Returns top ten products that were viewed along with the
        originating product.

        Args:
            sku: The product SKU.

        Returns:
            RecommendationsResponse containing also viewed products.
        """
        params = {"apiKey": self.client.options.api_key}
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/products/{sku}/alsoViewed.json",
            params=params,
        )
        response = self.client.request(request)
        return RecommendationsResponse.model_validate(response.json())

    def also_bought(
        self,
        sku: int | str,
    ) -> RecommendationsResponse:
        """Get products also bought with the specified product.

        Returns top ten products that were bought along with the
        originating product.

        Args:
            sku: The product SKU.

        Returns:
            RecommendationsResponse containing also bought products.
        """
        params = {"apiKey": self.client.options.api_key}
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/products/{sku}/alsoBought.json",
            params=params,
        )
        response = self.client.request(request)
        return RecommendationsResponse.model_validate(response.json())

    def viewed_ultimately_bought(
        self,
        sku: int | str,
    ) -> RecommendationsResponse:
        """Get products ultimately bought after viewing the specified product.

        Returns top ten products that were bought after having viewed
        the originating product.

        Args:
            sku: The product SKU.

        Returns:
            RecommendationsResponse containing viewed ultimately bought products.
        """
        params = {"apiKey": self.client.options.api_key}
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/products/{sku}/viewedUltimatelyBought.json",
            params=params,
        )
        response = self.client.request(request)
        return RecommendationsResponse.model_validate(response.json())


class AsyncRecommendationOperations(BaseOperations):
    """Async operations for the Recommendations API."""

    async def trending(
        self,
        category_id: Optional[str] = None,
    ) -> RecommendationsResponse:
        """Get trending products.

        Returns top ten products based on customer views over a rolling
        three hour time period.

        Args:
            category_id: Optional category ID to filter by.

        Returns:
            RecommendationsResponse containing trending products.
        """
        params = {"apiKey": self.client.options.api_key}
        if category_id:
            url = f"/v1/products/trendingViewed(categoryId={category_id}).json"
        else:
            url = "/v1/products/trendingViewed.json"
        request = self.client.client.build_request(
            method="GET",
            url=url,
            params=params,
        )
        response = await self.client.request(request)
        return RecommendationsResponse.model_validate(response.json())

    async def most_viewed(
        self,
        category_id: Optional[str] = None,
    ) -> RecommendationsResponse:
        """Get most viewed products.

        Returns top ten most frequently viewed products on BESTBUY.COM.

        Args:
            category_id: Optional category ID to filter by.

        Returns:
            RecommendationsResponse containing most viewed products.
        """
        params = {"apiKey": self.client.options.api_key}
        if category_id:
            url = f"/v1/products/mostViewed(categoryId={category_id}).json"
        else:
            url = "/v1/products/mostViewed.json"
        request = self.client.client.build_request(
            method="GET",
            url=url,
            params=params,
        )
        response = await self.client.request(request)
        return RecommendationsResponse.model_validate(response.json())

    async def also_viewed(
        self,
        sku: int | str,
    ) -> RecommendationsResponse:
        """Get products also viewed with the specified product.

        Returns top ten products that were viewed along with the
        originating product.

        Args:
            sku: The product SKU.

        Returns:
            RecommendationsResponse containing also viewed products.
        """
        params = {"apiKey": self.client.options.api_key}
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/products/{sku}/alsoViewed.json",
            params=params,
        )
        response = await self.client.request(request)
        return RecommendationsResponse.model_validate(response.json())

    async def also_bought(
        self,
        sku: int | str,
    ) -> RecommendationsResponse:
        """Get products also bought with the specified product.

        Returns top ten products that were bought along with the
        originating product.

        Args:
            sku: The product SKU.

        Returns:
            RecommendationsResponse containing also bought products.
        """
        params = {"apiKey": self.client.options.api_key}
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/products/{sku}/alsoBought.json",
            params=params,
        )
        response = await self.client.request(request)
        return RecommendationsResponse.model_validate(response.json())

    async def viewed_ultimately_bought(
        self,
        sku: int | str,
    ) -> RecommendationsResponse:
        """Get products ultimately bought after viewing the specified product.

        Returns top ten products that were bought after having viewed
        the originating product.

        Args:
            sku: The product SKU.

        Returns:
            RecommendationsResponse containing viewed ultimately bought products.
        """
        params = {"apiKey": self.client.options.api_key}
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/products/{sku}/viewedUltimatelyBought.json",
            params=params,
        )
        response = await self.client.request(request)
        return RecommendationsResponse.model_validate(response.json())


class StoreOperations(BaseOperations):
    """Operations for the Stores API."""

    def get(
        self,
        store_id: int,
        show: Optional[List[str]] = None,
    ) -> CatalogStore:
        """Get a single store by ID.

        Args:
            store_id: The Best Buy store ID.
            show: Optional list of attributes to return.

        Returns:
            The store details.
        """
        params = {"apiKey": self.client.options.api_key}
        if show:
            params["show"] = ",".join(show)
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/stores({store_id}).json",
            params=params,
        )
        response = self.client.request(request)
        data = response.json()
        if data.get("stores") and len(data["stores"]) > 0:
            return CatalogStore.model_validate(data["stores"][0])
        raise ValueError(f"Store {store_id} not found")

    def search(
        self,
        query: Optional[str] = None,
        show: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> CatalogStoresResponse:
        """Search for stores.

        Args:
            query: Search query string (e.g., "postalCode=55423").
            show: Optional list of attributes to return.
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).

        Returns:
            CatalogStoresResponse containing matching stores.
        """
        params = {
            "apiKey": self.client.options.api_key,
            "page": page,
            "pageSize": page_size,
        }
        if show:
            params["show"] = ",".join(show)
        url = "/v1/stores.json"
        if query:
            url = f"/v1/stores({query}).json"
        request = self.client.client.build_request(
            method="GET",
            url=url,
            params=params,
        )
        response = self.client.request(request)
        return CatalogStoresResponse.model_validate(response.json())

    def list(
        self,
        show: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> CatalogStoresResponse:
        """List all stores.

        Args:
            show: Optional list of attributes to return.
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).

        Returns:
            CatalogStoresResponse containing stores.
        """
        return self.search(
            query=None,
            show=show,
            page=page,
            page_size=page_size,
        )

    def search_by_area(
        self,
        postal_code: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        distance: int = 10,
        show: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> CatalogStoresResponse:
        """Search for stores within a specified area.

        Args:
            postal_code: ZIP code to search around.
            lat: Latitude to search around (use with lng).
            lng: Longitude to search around (use with lat).
            distance: Search radius in miles (default 10).
            show: Optional list of attributes to return.
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).

        Returns:
            CatalogStoresResponse containing nearby stores.
        """
        if postal_code:
            query = f"area({postal_code},{distance})"
        elif lat is not None and lng is not None:
            query = f"area({lat},{lng},{distance})"
        else:
            raise ValueError("Either postal_code or lat/lng must be provided")
        return self.search(
            query=query,
            show=show,
            page=page,
            page_size=page_size,
        )

    def search_pages(
        self,
        query: Optional[str] = None,
        show: Optional[List[str]] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> Paginator[CatalogStoresResponse, CatalogStore]:
        """Search for stores with automatic pagination.

        Args:
            query: Search query string (e.g., "postalCode=55423").
            show: Optional list of attributes to return.
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            Paginator for iterating over pages or stores.
        """

        def fetch_page(page: int) -> CatalogStoresResponse:
            return self.search(
                query=query,
                show=show,
                page=page,
                page_size=page_size,
            )

        return Paginator(
            fetch_page=fetch_page,
            items_attr="stores",
            page_size=page_size,
            max_pages=max_pages,
        )

    def list_pages(
        self,
        show: Optional[List[str]] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> Paginator[CatalogStoresResponse, CatalogStore]:
        """List all stores with automatic pagination.

        Args:
            show: Optional list of attributes to return.
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            Paginator for iterating over pages or stores.
        """
        return self.search_pages(
            query=None,
            show=show,
            page_size=page_size,
            max_pages=max_pages,
        )

    def search_by_area_pages(
        self,
        postal_code: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        distance: int = 10,
        show: Optional[List[str]] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> Paginator[CatalogStoresResponse, CatalogStore]:
        """Search for stores by area with automatic pagination.

        Args:
            postal_code: ZIP code to search around.
            lat: Latitude to search around (use with lng).
            lng: Longitude to search around (use with lat).
            distance: Search radius in miles (default 10).
            show: Optional list of attributes to return.
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            Paginator for iterating over pages or stores.
        """
        if postal_code:
            query = f"area({postal_code},{distance})"
        elif lat is not None and lng is not None:
            query = f"area({lat},{lng},{distance})"
        else:
            raise ValueError("Either postal_code or lat/lng must be provided")
        return self.search_pages(
            query=query,
            show=show,
            page_size=page_size,
            max_pages=max_pages,
        )


class AsyncStoreOperations(BaseOperations):
    """Async operations for the Stores API."""

    async def get(
        self,
        store_id: int,
        show: Optional[List[str]] = None,
    ) -> CatalogStore:
        """Get a single store by ID.

        Args:
            store_id: The Best Buy store ID.
            show: Optional list of attributes to return.

        Returns:
            The store details.
        """
        params = {"apiKey": self.client.options.api_key}
        if show:
            params["show"] = ",".join(show)
        request = self.client.client.build_request(
            method="GET",
            url=f"/v1/stores({store_id}).json",
            params=params,
        )
        response = await self.client.request(request)
        data = response.json()
        if data.get("stores") and len(data["stores"]) > 0:
            return CatalogStore.model_validate(data["stores"][0])
        raise ValueError(f"Store {store_id} not found")

    async def search(
        self,
        query: Optional[str] = None,
        show: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> CatalogStoresResponse:
        """Search for stores.

        Args:
            query: Search query string (e.g., "postalCode=55423").
            show: Optional list of attributes to return.
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).

        Returns:
            CatalogStoresResponse containing matching stores.
        """
        params = {
            "apiKey": self.client.options.api_key,
            "page": page,
            "pageSize": page_size,
        }
        if show:
            params["show"] = ",".join(show)
        url = "/v1/stores.json"
        if query:
            url = f"/v1/stores({query}).json"
        request = self.client.client.build_request(
            method="GET",
            url=url,
            params=params,
        )
        response = await self.client.request(request)
        return CatalogStoresResponse.model_validate(response.json())

    async def list(
        self,
        show: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> CatalogStoresResponse:
        """List all stores.

        Args:
            show: Optional list of attributes to return.
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).

        Returns:
            CatalogStoresResponse containing stores.
        """
        return await self.search(
            query=None,
            show=show,
            page=page,
            page_size=page_size,
        )

    async def search_by_area(
        self,
        postal_code: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        distance: int = 10,
        show: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> CatalogStoresResponse:
        """Search for stores within a specified area.

        Args:
            postal_code: ZIP code to search around.
            lat: Latitude to search around (use with lng).
            lng: Longitude to search around (use with lat).
            distance: Search radius in miles (default 10).
            show: Optional list of attributes to return.
            page: Page number (1-indexed).
            page_size: Number of results per page (max 100).

        Returns:
            CatalogStoresResponse containing nearby stores.
        """
        if postal_code:
            query = f"area({postal_code},{distance})"
        elif lat is not None and lng is not None:
            query = f"area({lat},{lng},{distance})"
        else:
            raise ValueError("Either postal_code or lat/lng must be provided")
        return await self.search(
            query=query,
            show=show,
            page=page,
            page_size=page_size,
        )

    def search_pages(
        self,
        query: Optional[str] = None,
        show: Optional[List[str]] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> AsyncPaginator[CatalogStoresResponse, CatalogStore]:
        """Search for stores with automatic pagination.

        Args:
            query: Search query string (e.g., "postalCode=55423").
            show: Optional list of attributes to return.
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            AsyncPaginator for iterating over pages or stores.
        """

        async def fetch_page(page: int) -> CatalogStoresResponse:
            return await self.search(
                query=query,
                show=show,
                page=page,
                page_size=page_size,
            )

        return AsyncPaginator(
            fetch_page=fetch_page,
            items_attr="stores",
            page_size=page_size,
            max_pages=max_pages,
        )

    def list_pages(
        self,
        show: Optional[List[str]] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> AsyncPaginator[CatalogStoresResponse, CatalogStore]:
        """List all stores with automatic pagination.

        Args:
            show: Optional list of attributes to return.
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            AsyncPaginator for iterating over pages or stores.
        """
        return self.search_pages(
            query=None,
            show=show,
            page_size=page_size,
            max_pages=max_pages,
        )

    def search_by_area_pages(
        self,
        postal_code: Optional[str] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        distance: int = 10,
        show: Optional[List[str]] = None,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ) -> AsyncPaginator[CatalogStoresResponse, CatalogStore]:
        """Search for stores by area with automatic pagination.

        Args:
            postal_code: ZIP code to search around.
            lat: Latitude to search around (use with lng).
            lng: Longitude to search around (use with lat).
            distance: Search radius in miles (default 10).
            show: Optional list of attributes to return.
            page_size: Number of results per page (max 100).
            max_pages: Maximum number of pages to fetch (None for all).

        Returns:
            AsyncPaginator for iterating over pages or stores.
        """
        if postal_code:
            query = f"area({postal_code},{distance})"
        elif lat is not None and lng is not None:
            query = f"area({lat},{lng},{distance})"
        else:
            raise ValueError("Either postal_code or lat/lng must be provided")
        return self.search_pages(
            query=query,
            show=show,
            page_size=page_size,
            max_pages=max_pages,
        )
