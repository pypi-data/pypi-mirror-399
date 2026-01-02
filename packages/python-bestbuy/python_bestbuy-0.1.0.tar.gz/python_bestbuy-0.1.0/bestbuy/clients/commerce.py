from typing import Any, Dict

import httpx

from ..configs import CommerceConfig
from ..operations.commerce import (
    AsyncAuthOperations,
    AsyncEncryptionOperations,
    AsyncFulfillmentOperations,
    AsyncOrderOperations,
    AsyncPricingOperations,
    AuthOperations,
    EncryptionOperations,
    FulfillmentOperations,
    OrderOperations,
    PricingOperations,
)
from .base import AsyncClient, Client


class CommerceClient(Client):
    config_parser = CommerceConfig
    options: CommerceConfig

    def __init__(
        self,
        client: httpx.Client | None = None,
        options: Dict[str, Any] | CommerceConfig | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(client, options, **kwargs)
        self.auth = AuthOperations(self)
        self.fulfillment = FulfillmentOperations(self)
        self.pricing = PricingOperations(self)
        self.orders = OrderOperations(self)
        self.encryption = EncryptionOperations(self)

    @property
    def base_url(self):
        if self.options.base_url is not None:
            return self.options.base_url
        return (
            "https://commerce-ssl.sandbox.bestbuy.com"
            if self.options.sandbox is True
            else "https://commerce-ssl.bestbuy.com"
        )


class AsyncCommerceClient(AsyncClient):
    config_parser = CommerceConfig
    options: CommerceConfig

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        options: Dict[str, Any] | CommerceConfig | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(client, options, **kwargs)
        self.auth = AsyncAuthOperations(self)
        self.fulfillment = AsyncFulfillmentOperations(self)
        self.pricing = AsyncPricingOperations(self)
        self.orders = AsyncOrderOperations(self)
        self.encryption = AsyncEncryptionOperations(self)

    @property
    def base_url(self):
        if self.options.base_url is not None:
            return self.options.base_url
        return (
            "https://commerce-ssl.sandbox.bestbuy.com"
            if self.options.sandbox is True
            else "https://commerce-ssl.bestbuy.com"
        )
