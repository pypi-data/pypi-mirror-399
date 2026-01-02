from .base import BaseConfig


class CatalogConfig(BaseConfig):
    base_url: str = "https://api.bestbuy.com"
    content_type: str = "application/json"
