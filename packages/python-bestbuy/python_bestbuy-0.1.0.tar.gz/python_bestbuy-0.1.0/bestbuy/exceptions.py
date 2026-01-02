"""Custom exceptions for the Best Buy API client."""


class BestBuyError(Exception):
    """Base exception for all Best Buy API errors."""

    pass


class ConfigError(BestBuyError):
    """Raised when there's an error with client configuration."""

    pass


class AuthenticationError(BestBuyError):
    """Raised when authentication fails."""

    pass


class SessionRequiredError(BestBuyError):
    """Raised when an operation requires an active session but none exists."""

    pass


class APIError(BestBuyError):
    """Raised when the API returns an error.

    Used to handle errors from both Commerce and Catalog APIs.

    Attributes:
        message: Human-readable error message
        code: Error code from the API (if available)
        sku: SKU that caused the error (if available)
        response_text: Raw response text (XML or JSON)
    """

    def __init__(
        self,
        message: str,
        code: str | None = None,
        sku: str | None = None,
        response_text: str | None = None,
    ):
        self.message = message
        self.code = code
        self.sku = sku
        self.response_text = response_text

        # Build error message
        parts = [message]
        if code:
            parts.append(f"Error code: {code}")
        if sku:
            parts.append(f"SKU: {sku}")

        super().__init__(" | ".join(parts))
