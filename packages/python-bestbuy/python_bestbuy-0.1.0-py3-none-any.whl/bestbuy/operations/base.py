"""Base classes for Best Buy API operations."""

from typing import Any


class BaseOperations:
    """Base class for all API operations (sync and async)."""

    def __init__(self, client: Any) -> None:
        self.client = client
