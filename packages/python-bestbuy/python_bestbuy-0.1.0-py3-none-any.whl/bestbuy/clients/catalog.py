from typing import Any, Dict

import httpx

from ..configs import CatalogConfig
from ..operations.catalog import (
    AsyncCategoryOperations,
    AsyncProductOperations,
    AsyncRecommendationOperations,
    AsyncStoreOperations,
    CategoryOperations,
    ProductOperations,
    RecommendationOperations,
    StoreOperations,
)
from .base import AsyncClient, Client


class CatalogClient(Client):
    """Synchronous client for the Best Buy Catalog API."""

    config_parser = CatalogConfig

    def __init__(
        self,
        client: httpx.Client | None = None,
        options: Dict[str, Any] | CatalogConfig | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(client, options, **kwargs)
        self.products = ProductOperations(self)
        self.categories = CategoryOperations(self)
        self.recommendations = RecommendationOperations(self)
        self.stores = StoreOperations(self)

    @property
    def base_url(self):
        if self.options.base_url is not None:
            return self.options.base_url
        return "https://api.bestbuy.com"


class AsyncCatalogClient(AsyncClient):
    """Asynchronous client for the Best Buy Catalog API."""

    config_parser = CatalogConfig

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        options: Dict[str, Any] | CatalogConfig | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(client, options, **kwargs)
        self.products = AsyncProductOperations(self)
        self.categories = AsyncCategoryOperations(self)
        self.recommendations = AsyncRecommendationOperations(self)
        self.stores = AsyncStoreOperations(self)

    @property
    def base_url(self):
        if self.options.base_url is not None:
            return self.options.base_url
        return "https://api.bestbuy.com"
