from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from ..clients.commerce import AsyncCommerceClient, CommerceClient

from .base import BaseOperations
from ..exceptions import AuthenticationError, SessionRequiredError
from ..models import (
    AvailabilityQueryRequest,
    AvailabilityQueryResponse,
    CommerceResponse,
    DeliveryOptionsResponse,
    DeliveryServicesResponse,
    OrderQueryRequest,
    OrderResponse,
    OrderSubmitGuestRequest,
    OrderSubmitRegisteredRequest,
    PriceQueryRequest,
    PriceResponse,
    ProductServiceRequest,
    ProductServiceResponse,
    PublicKeyEncryptionResponse,
    ShippingAddress,
    ShippingOptionsResponse,
    ShippingQueryRequest,
    ShippingQueryItem,
    StoresResponse,
)


class _AuthContext:
    """Context manager for authenticated Commerce API sessions.

    Automatically handles login on entry and logout on exit.
    """

    def __init__(
        self,
        auth_ops: "AuthOperations",
        username: str | None = None,
        password: str | None = None,
    ):
        self.auth_ops = auth_ops
        self.username = username
        self.password = password

    def __enter__(self) -> "CommerceClient":
        self.auth_ops.login(self.username, self.password)
        return self.auth_ops.client

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if "X-SESSION-ID" in self.auth_ops.client.client.headers:
            try:
                self.auth_ops.logout()
            except Exception:
                pass


class _AsyncAuthContext:
    """Async context manager for authenticated Commerce API sessions.

    Automatically handles login on entry and logout on exit.
    """

    def __init__(
        self,
        auth_ops: "AsyncAuthOperations",
        username: str | None = None,
        password: str | None = None,
    ):
        self.auth_ops = auth_ops
        self.username = username
        self.password = password

    async def __aenter__(self) -> "AsyncCommerceClient":
        await self.auth_ops.login(self.username, self.password)
        return self.auth_ops.client

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if "X-SESSION-ID" in self.auth_ops.client.client.headers:
            try:
                await self.auth_ops.logout()
            except Exception:
                pass


class CommerceOperations(BaseOperations):
    """Base class for commerce operations that may require session."""

    def _require_session(self) -> None:
        if "X-SESSION-ID" not in self.client.client.headers:
            raise SessionRequiredError(
                "Must be logged in to perform this operation. "
                "Use client.auth.login() to obtain a session."
            )


class AuthOperations(CommerceOperations):
    """Operations for Commerce API authentication.

    Handles login and logout for Registered Orders. Before placing a Registered
    Order (charged to your company credit card), you must first authenticate
    using HTTP Basic Authentication with your Billing Account credentials.

    Sessions are valid for 30 minutes.

    Example:
        # Using context manager (recommended)
        with client.auth:
            order_response = client.orders.submit_registered(order)

        # Or with explicit credentials
        with client.auth(username="user", password="pass"):
            order_response = client.orders.submit_registered(order)

        # Manual login/logout
        client.auth.login()
        try:
            order_response = client.orders.submit_registered(order)
        finally:
            client.auth.logout()
    """

    def login(
        self, username: str | None = None, password: str | None = None
    ) -> CommerceResponse:
        """Authenticate with the Commerce API to obtain a session.

        Uses HTTP Basic Authentication with your Billing Account credentials.
        The returned session ID is automatically stored in the client headers
        and used for subsequent requests.

        Args:
            username: Billing Account username. If not provided, uses the
                username from client options.
            password: Billing Account password. If not provided, uses the
                password from client options.

        Returns:
            CommerceResponse containing links to available endpoints.

        Raises:
            AuthenticationError: If username or password is not provided,
                or if the login response does not contain a session ID.

        Note:
            Sessions are valid for 30 minutes of inactivity.
        """
        auth_username = username or self.client.options.username
        auth_password = password or self.client.options.password
        if not auth_username or not auth_password:
            raise AuthenticationError("Username and password required for login")

        # Build auth header manually since build_request doesn't accept auth param
        auth = httpx.BasicAuth(username=auth_username, password=auth_password)
        auth_header = auth._auth_header

        request = self.client.client.build_request(
            method="GET", url="/commerce/login", headers={"Authorization": auth_header}
        )
        response = self.client.request(request)
        session_id = response.headers.get("X-SESSION-ID")
        if not session_id:
            raise AuthenticationError("No X-SESSION-ID header in login response")
        self.client.client.headers["X-SESSION-ID"] = session_id
        return CommerceResponse.from_xml(response.text)

    def logout(self) -> None:
        """Invalidate the current session.

        After placing an order, use this endpoint to immediately invalidate
        the X-SESSION-ID. The session ID is removed from the client headers
        regardless of whether the logout request succeeds.

        If no session is active, this method does nothing.
        """
        if "X-SESSION-ID" not in self.client.client.headers:
            return

        try:
            if self.client.options.auto_logout:
                request = self.client.client.build_request(
                    method="POST", url="/commerce/logout"
                )
                self.client.request(request)
        finally:
            # Always remove session ID header, even if auto_logout is False or request fails
            del self.client.client.headers["X-SESSION-ID"]

    def __call__(
        self, username: str | None = None, password: str | None = None
    ) -> _AuthContext:
        """Create an authentication context with optional credentials.

        Args:
            username: Billing Account username.
            password: Billing Account password.

        Returns:
            Context manager that handles login/logout automatically.
        """
        return _AuthContext(self, username, password)

    def __enter__(self) -> "CommerceClient":
        self.login()
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if "X-SESSION-ID" in self.client.client.headers:
            try:
                self.logout()
            except Exception:
                pass


class AsyncAuthOperations(CommerceOperations):
    """Async operations for Commerce API authentication.

    Handles login and logout for Registered Orders. Before placing a Registered
    Order (charged to your company credit card), you must first authenticate
    using HTTP Basic Authentication with your Billing Account credentials.

    Sessions are valid for 30 minutes.

    Example:
        # Using async context manager (recommended)
        async with client.auth:
            order_response = await client.orders.submit_registered(order)

        # Or with explicit credentials
        async with client.auth(username="user", password="pass"):
            order_response = await client.orders.submit_registered(order)
    """

    def __call__(
        self, username: str | None = None, password: str | None = None
    ) -> "_AsyncAuthContext":
        """Create an authentication context with optional credentials.

        Args:
            username: Billing Account username.
            password: Billing Account password.

        Returns:
            Async context manager that handles login/logout automatically.
        """
        return _AsyncAuthContext(self, username, password)

    async def login(
        self, username: str | None = None, password: str | None = None
    ) -> CommerceResponse:
        """Authenticate with the Commerce API to obtain a session.

        Uses HTTP Basic Authentication with your Billing Account credentials.
        The returned session ID is automatically stored in the client headers
        and used for subsequent requests.

        Args:
            username: Billing Account username. If not provided, uses the
                username from client options.
            password: Billing Account password. If not provided, uses the
                password from client options.

        Returns:
            CommerceResponse containing links to available endpoints.

        Raises:
            AuthenticationError: If username or password is not provided,
                or if the login response does not contain a session ID.

        Note:
            Sessions are valid for 30 minutes of inactivity.
        """
        auth_username = username or self.client.options.username
        auth_password = password or self.client.options.password
        if not auth_username or not auth_password:
            raise AuthenticationError("Username and password required for login")

        # Build auth header manually since build_request doesn't accept auth param
        auth = httpx.BasicAuth(username=auth_username, password=auth_password)
        auth_header = auth._auth_header

        request = self.client.client.build_request(
            method="GET", url="/commerce/login", headers={"Authorization": auth_header}
        )
        response = await self.client.request(request)
        session_id = response.headers.get("X-SESSION-ID")
        if not session_id:
            raise AuthenticationError("No X-SESSION-ID header in login response")
        self.client.client.headers["X-SESSION-ID"] = session_id
        return CommerceResponse.from_xml(response.text)

    async def logout(self) -> None:
        """Invalidate the current session.

        After placing an order, use this endpoint to immediately invalidate
        the X-SESSION-ID. The session ID is removed from the client headers
        regardless of whether the logout request succeeds.

        If no session is active, this method does nothing.
        """
        if "X-SESSION-ID" not in self.client.client.headers:
            return  # No session to logout from

        try:
            if self.client.options.auto_logout:
                request = self.client.client.build_request(
                    method="POST", url="/commerce/logout"
                )
                await self.client.request(request)
        finally:
            # Always remove session ID header, even if auto_logout is False or request fails
            del self.client.client.headers["X-SESSION-ID"]

    async def __aenter__(self) -> "AsyncCommerceClient":
        await self.login()
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if "X-SESSION-ID" in self.client.client.headers:
            try:
                await self.logout()
            except Exception:
                pass


class FulfillmentOperations(CommerceOperations):
    """Operations for checking product fulfillment options.

    Provides methods to check product availability, shipping options,
    store pickup availability, and home delivery options.
    """

    def check_availability(self, sku: str | int) -> AvailabilityQueryResponse:
        """Check the types of fulfillment options available for a SKU.

        Retrieves whether a product can be shipped to a customer's address,
        delivered to their home (for large items), or picked up at a store.

        Args:
            sku: The Best Buy SKU to check availability for.

        Returns:
            AvailabilityQueryResponse containing:
            - shipping_eligible: Whether the item can be shipped
            - delivery_eligible: Whether home delivery is available
            - pickup_eligible: Whether store pickup is available
            - max_quantity: Maximum quantity that can be ordered
        """
        query = AvailabilityQueryRequest(sku_id=str(sku))
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/productavailability",
            content=query.to_xml(encoding="unicode"),
        )
        response = self.client.request(request)
        return AvailabilityQueryResponse.from_xml(response.text)

    def get_shipping_options(
        self,
        sku: str | int,
        address1: str,
        city: str,
        state: str,
        postalcode: str,
        address2: str = "",
        country: str = "US",
    ) -> ShippingOptionsResponse:
        """Get available shipping service levels and costs for a SKU.

        Retrieves shipping options (e.g., standard, expedited) with pricing
        and expected delivery dates for shipping a product to the given address.

        Args:
            sku: The Best Buy SKU to get shipping options for.
            address1: Primary street address.
            city: City name.
            state: Two-letter state code (e.g., "CA", "NY").
            postalcode: ZIP code.
            address2: Secondary address line (apartment, suite, etc.).
            country: Two-letter country code. Defaults to "US".

        Returns:
            ShippingOptionsResponse containing available shipping methods,
            each with a shipping_option_key to use when submitting orders.
        """
        query = ShippingQueryRequest(
            address=ShippingAddress(
                address1=address1,
                address2=address2,
                city=city,
                state=state,
                postalcode=postalcode,
                country=country,
            ),
            item=ShippingQueryItem(sku=str(sku)),
        )
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/shippingoption",
            content=query.to_xml(encoding="unicode"),
        )
        response = self.client.request(request)
        return ShippingOptionsResponse.from_xml(response.text)

    def find_stores(
        self, sku: str | int, zip_code: str, store_count: int = 6
    ) -> StoresResponse:
        """Find stores near a ZIP code where a SKU can be picked up.

        Retrieves Best Buy stores close to the given ZIP code that have
        the product available for pickup (in-store or ship-to-store).

        Args:
            sku: The Best Buy SKU to check store availability for.
            zip_code: ZIP code to search near.
            store_count: Maximum number of stores to return. Defaults to 6.

        Returns:
            StoresResponse containing store locations with pickup availability
            and ship-to-store options.
        """
        request = self.client.client.build_request(
            method="GET",
            url="/commerce/store",
            params={"skuid": str(sku), "zipcode": zip_code, "storecount": store_count},
        )
        response = self.client.request(request)
        return StoresResponse.from_xml(response.text)

    def get_delivery_options(
        self, sku: str | int, zip_code: str, delivery_service_id: str | None = None
    ) -> DeliveryOptionsResponse:
        """Get available delivery time slots for home delivery items.

        For large items that require home delivery (appliances, TVs, etc.),
        retrieves available delivery dates and time windows. Customer must
        be present during the scheduled delivery window.

        Args:
            sku: The Best Buy SKU to get delivery options for.
            zip_code: ZIP code for delivery location.
            delivery_service_id: Optional delivery service ID to filter options
                (e.g., for installation or haul away services).

        Returns:
            DeliveryOptionsResponse containing available delivery time slots
            with date, start time, and end time for each option.
        """
        params = {"sku": str(sku), "zipcode": zip_code}
        if delivery_service_id:
            params["deliveryServiceId"] = delivery_service_id

        request = self.client.client.build_request(
            method="GET",
            url="/commerce/delivery-options",
            params=params,
        )
        response = self.client.request(request)
        return DeliveryOptionsResponse.from_xml(response.text)

    def get_delivery_services(
        self, sku: str | int, zip_code: str
    ) -> DeliveryServicesResponse:
        """Get available delivery services for a SKU.

        Retrieves additional services available for home delivery items,
        such as installation, hookup, and haul away of old appliances.

        Args:
            sku: The Best Buy SKU to get delivery services for.
            zip_code: ZIP code for delivery location.

        Returns:
            DeliveryServicesResponse containing available services with
            descriptions and pricing.
        """
        request = self.client.client.build_request(
            method="GET",
            url="/commerce/delivery-services",
            params={"sku": str(sku), "zipcode": zip_code},
        )
        response = self.client.request(request)
        return DeliveryServicesResponse.from_xml(response.text)


class AsyncFulfillmentOperations(CommerceOperations):
    """Async operations for checking product fulfillment options.

    Provides async methods to check product availability, shipping options,
    store pickup availability, and home delivery options.
    """

    async def check_availability(self, sku: str | int) -> AvailabilityQueryResponse:
        """Check the types of fulfillment options available for a SKU.

        Retrieves whether a product can be shipped to a customer's address,
        delivered to their home (for large items), or picked up at a store.

        Args:
            sku: The Best Buy SKU to check availability for.

        Returns:
            AvailabilityQueryResponse containing:
            - shipping_eligible: Whether the item can be shipped
            - delivery_eligible: Whether home delivery is available
            - pickup_eligible: Whether store pickup is available
            - max_quantity: Maximum quantity that can be ordered
        """
        query = AvailabilityQueryRequest(sku_id=str(sku))
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/productavailability",
            content=query.to_xml(encoding="unicode"),
        )
        response = await self.client.request(request)
        return AvailabilityQueryResponse.from_xml(response.text)

    async def get_shipping_options(
        self,
        sku: str | int,
        address1: str,
        city: str,
        state: str,
        postalcode: str,
        address2: str = "",
        country: str = "US",
    ) -> ShippingOptionsResponse:
        """Get available shipping service levels and costs for a SKU.

        Retrieves shipping options (e.g., standard, expedited) with pricing
        and expected delivery dates for shipping a product to the given address.

        Args:
            sku: The Best Buy SKU to get shipping options for.
            address1: Primary street address.
            city: City name.
            state: Two-letter state code (e.g., "CA", "NY").
            postalcode: ZIP code.
            address2: Secondary address line (apartment, suite, etc.).
            country: Two-letter country code. Defaults to "US".

        Returns:
            ShippingOptionsResponse containing available shipping methods,
            each with a shipping_option_key to use when submitting orders.
        """
        query = ShippingQueryRequest(
            address=ShippingAddress(
                address1=address1,
                address2=address2,
                city=city,
                state=state,
                postalcode=postalcode,
                country=country,
            ),
            item=ShippingQueryItem(sku=str(sku)),
        )
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/shippingoption",
            content=query.to_xml(encoding="unicode"),
        )
        response = await self.client.request(request)
        return ShippingOptionsResponse.from_xml(response.text)

    async def find_stores(
        self, sku: str | int, zip_code: str, store_count: int = 6
    ) -> StoresResponse:
        """Find stores near a ZIP code where a SKU can be picked up.

        Retrieves Best Buy stores close to the given ZIP code that have
        the product available for pickup (in-store or ship-to-store).

        Args:
            sku: The Best Buy SKU to check store availability for.
            zip_code: ZIP code to search near.
            store_count: Maximum number of stores to return. Defaults to 6.

        Returns:
            StoresResponse containing store locations with pickup availability
            and ship-to-store options.
        """
        request = self.client.client.build_request(
            method="GET",
            url="/commerce/store",
            params={"skuid": str(sku), "zipcode": zip_code, "storecount": store_count},
        )
        response = await self.client.request(request)
        return StoresResponse.from_xml(response.text)

    async def get_delivery_options(
        self, sku: str | int, zip_code: str, delivery_service_id: str | None = None
    ) -> DeliveryOptionsResponse:
        """Get available delivery time slots for home delivery items.

        For large items that require home delivery (appliances, TVs, etc.),
        retrieves available delivery dates and time windows. Customer must
        be present during the scheduled delivery window.

        Args:
            sku: The Best Buy SKU to get delivery options for.
            zip_code: ZIP code for delivery location.
            delivery_service_id: Optional delivery service ID to filter options
                (e.g., for installation or haul away services).

        Returns:
            DeliveryOptionsResponse containing available delivery time slots
            with date, start time, and end time for each option.
        """
        params = {"sku": str(sku), "zipcode": zip_code}
        if delivery_service_id:
            params["deliveryServiceId"] = delivery_service_id

        request = self.client.client.build_request(
            method="GET",
            url="/commerce/delivery-options",
            params=params,
        )
        response = await self.client.request(request)
        return DeliveryOptionsResponse.from_xml(response.text)

    async def get_delivery_services(
        self, sku: str | int, zip_code: str
    ) -> DeliveryServicesResponse:
        """Get available delivery services for a SKU.

        Retrieves additional services available for home delivery items,
        such as installation, hookup, and haul away of old appliances.

        Args:
            sku: The Best Buy SKU to get delivery services for.
            zip_code: ZIP code for delivery location.

        Returns:
            DeliveryServicesResponse containing available services with
            descriptions and pricing.
        """
        request = self.client.client.build_request(
            method="GET",
            url="/commerce/delivery-services",
            params={"sku": str(sku), "zipcode": zip_code},
        )
        response = await self.client.request(request)
        return DeliveryServicesResponse.from_xml(response.text)


class PricingOperations(CommerceOperations):
    """Operations for retrieving product pricing information."""

    def get_unit_price(self, sku: str | int) -> PriceResponse:
        """Get the current price for a single unit of a SKU.

        Retrieves the current retail price for a product. Use this to
        display accurate pricing before adding items to an order.

        Args:
            sku: The Best Buy SKU to get pricing for.

        Returns:
            PriceResponse containing the current unit price.
        """
        query = PriceQueryRequest(sku_id=str(sku))
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/unitprice",
            content=query.to_xml(encoding="unicode"),
        )
        response = self.client.request(request)
        return PriceResponse.from_xml(response.text)

    def get_product_service(
        self, sku: str | int, zip_code: str
    ) -> ProductServiceResponse:
        """Get combined product information in a single request.

        Retrieves availability, pricing, shipping options, and store
        availability all in one API call. This is more efficient than
        making separate calls to individual endpoints.

        Args:
            sku: The Best Buy SKU to get information for.
            zip_code: ZIP code for location-specific data (shipping, stores).

        Returns:
            ProductServiceResponse containing availability, price, shipping
            options, and nearby store information.

        Note:
            Tax data from this endpoint is deprecated. Use order review
            for accurate tax calculations.
        """
        request_data = ProductServiceRequest(skuid=str(sku), zipcode=zip_code)
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/productservice",
            content=request_data.to_xml(encoding="unicode"),
        )
        response = self.client.request(request)
        return ProductServiceResponse.from_xml(response.text)


class AsyncPricingOperations(CommerceOperations):
    """Async operations for retrieving product pricing information."""

    async def get_unit_price(self, sku: str | int) -> PriceResponse:
        """Get the current price for a single unit of a SKU.

        Retrieves the current retail price for a product. Use this to
        display accurate pricing before adding items to an order.

        Args:
            sku: The Best Buy SKU to get pricing for.

        Returns:
            PriceResponse containing the current unit price.
        """
        query = PriceQueryRequest(sku_id=str(sku))
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/unitprice",
            content=query.to_xml(encoding="unicode"),
        )
        response = await self.client.request(request)
        return PriceResponse.from_xml(response.text)

    async def get_product_service(
        self, sku: str | int, zip_code: str
    ) -> ProductServiceResponse:
        """Get combined product information in a single request.

        Retrieves availability, pricing, shipping options, and store
        availability all in one API call. This is more efficient than
        making separate calls to individual endpoints.

        Args:
            sku: The Best Buy SKU to get information for.
            zip_code: ZIP code for location-specific data (shipping, stores).

        Returns:
            ProductServiceResponse containing availability, price, shipping
            options, and nearby store information.

        Note:
            Tax data from this endpoint is deprecated. Use order review
            for accurate tax calculations.
        """
        request_data = ProductServiceRequest(skuid=str(sku), zipcode=zip_code)
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/productservice",
            content=request_data.to_xml(encoding="unicode"),
        )
        response = await self.client.request(request)
        return ProductServiceResponse.from_xml(response.text)


class OrderOperations(CommerceOperations):
    """Operations for order management.

    Provides methods to submit, review, and query orders. Supports both
    Registered Orders (charged to company credit card) and Guest Orders
    (charged to customer's credit card).

    For Registered Orders, you must first authenticate using client.auth.login()
    or use the auth context manager.
    """

    def submit_registered(
        self, order: OrderSubmitRegisteredRequest
    ) -> OrderResponse | OrderSubmitRegisteredRequest:
        """Submit a Registered Order.

        Places an order that will be charged to your company's credit card
        stored in your Billing Account. Requires an active session obtained
        via login.

        Args:
            order: The order details including items, fulfillment options,
                and tender information.

        Returns:
            If reviewable=False (default): Returns OrderResponse with full
                order details retrieved from the API after order creation.
            If reviewable=True: Returns the input order unchanged (order was
                validated but not created).

        Raises:
            SessionRequiredError: If not logged in.

        Example:
            with client.auth:
                response = client.orders.submit_registered(order)
        """
        self._require_session()
        if self.client.options.partner_id and not order.partner_id:
            order.partner_id = self.client.options.partner_id
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/order/submit",
            content=order.to_xml(encoding="unicode", skip_empty=True),
        )
        response = self.client.request(request)

        # If reviewable=true and 200 OK, order was validated but not created
        if order.reviewable and response.status_code == 200:
            return order

        # If reviewable=false and 201 Created, retrieve order from Location header
        if response.status_code == 201:
            location = response.headers.get("Location", "")
            # Extract order ID from Location URL (e.g., /commerce/order/BBY01-123456789)
            order_id = location.rstrip("/").split("/")[-1]
            if order_id:
                return self.lookup(order_id)

        return order

    def review(
        self, order: OrderSubmitRegisteredRequest | OrderSubmitGuestRequest
    ) -> OrderResponse:
        """Review an order and get accurate tax calculations before submitting.

        Always use this endpoint before submitting an order to get the
        most accurate tax calculation. Set reviewable="true" in the order.

        Args:
            order: The order details to review (registered or guest order).
                Should have reviewable="true".

        Returns:
            OrderResponse containing the order with calculated taxes
            and validated item information.

        Raises:
            SessionRequiredError: If not logged in.

        Note:
            This is the recommended method for accurate tax calculations.
            The deprecated /commerce/tax endpoint should not be used.
        """
        self._require_session()
        if self.client.options.partner_id and not order.partner_id:
            order.partner_id = self.client.options.partner_id
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/order/review",
            content=order.to_xml(encoding="unicode", skip_empty=True),
        )
        response = self.client.request(request)
        return OrderResponse.from_xml(response.text)

    def submit_guest(
        self, order: OrderSubmitGuestRequest
    ) -> OrderResponse | OrderSubmitGuestRequest:
        """Submit a Guest Order.

        Places an order that will be charged to the customer's credit card.
        No session is required. The credit card information must be encrypted
        using the public key from get_encryption_key().

        Args:
            order: The order details including items, fulfillment options,
                and encrypted payment information.

        Returns:
            If reviewable=False (default) and a session is active: Returns
                OrderResponse with full order details retrieved from the API.
            If reviewable=False but no session: Returns the input order unchanged
                (order was created but details cannot be retrieved without session).
            If reviewable=True: Returns the input order unchanged (order was
                validated but not created).

        Note:
            Use client.encryption.get_encryption_key() to obtain the
            public key for encrypting credit card data. Retrieving order
            details after submission requires an active session.
        """
        if self.client.options.partner_id and not order.partner_id:
            order.partner_id = self.client.options.partner_id
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/guestuser",
            content=order.to_xml(encoding="unicode", skip_empty=True),
        )
        response = self.client.request(request)

        # If reviewable=true and 200 OK, order was validated but not created
        if order.reviewable and response.status_code == 200:
            return order

        # If reviewable=false and 201 Created, retrieve order from Location header
        if response.status_code == 201:
            location = response.headers.get("Location", "")
            # Extract order ID from Location URL (e.g., /commerce/order/BBY01-123456789)
            order_id = location.rstrip("/").split("/")[-1]
            # Only retrieve if we have a session and an order ID
            if order_id and "X-SESSION-ID" in self.client.client.headers:
                return self.lookup(order_id)

        return order

    def query(self, order_id: str, last_name: str, phone_number: str) -> OrderResponse:
        """Look up an order by ID, last name, and phone number.

        Allows customers to check their order status without authentication.
        All three parameters must match the original order.

        Args:
            order_id: The Best Buy order ID.
            last_name: Customer's last name from the order.
            phone_number: Customer's phone number from the order.

        Returns:
            OrderResponse containing the order details and status.
        """
        query = OrderQueryRequest(
            order_id=order_id, last_name=last_name, phone_number=phone_number
        )
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/order/query",
            content=query.to_xml(encoding="unicode"),
        )
        response = self.client.request(request)
        return OrderResponse.from_xml(response.text)

    def lookup(self, order_id: str) -> OrderResponse:
        """Look up an order by Best Buy order ID.

        Retrieves order details for a Registered Order. Requires an
        active session.

        Args:
            order_id: The Best Buy order ID returned when the order
                was submitted.

        Returns:
            OrderResponse containing the order details and status.

        Raises:
            SessionRequiredError: If not logged in.
        """
        self._require_session()
        request = self.client.client.build_request(
            method="GET",
            url=f"/commerce/order/{order_id}",
        )
        response = self.client.request(request)
        return OrderResponse.from_xml(response.text)


class AsyncOrderOperations(CommerceOperations):
    """Async operations for order management.

    Provides async methods to submit, review, and query orders. Supports both
    Registered Orders (charged to company credit card) and Guest Orders
    (charged to customer's credit card).

    For Registered Orders, you must first authenticate using client.auth.login()
    or use the auth context manager.
    """

    async def submit_registered(
        self, order: OrderSubmitRegisteredRequest
    ) -> OrderResponse | OrderSubmitRegisteredRequest:
        """Submit a Registered Order.

        Places an order that will be charged to your company's credit card
        stored in your Billing Account. Requires an active session obtained
        via login.

        Args:
            order: The order details including items, fulfillment options,
                and tender information.

        Returns:
            If reviewable=False (default): Returns OrderResponse with full
                order details retrieved from the API after order creation.
            If reviewable=True: Returns the input order unchanged (order was
                validated but not created).

        Raises:
            SessionRequiredError: If not logged in.

        Example:
            async with client.auth:
                response = await client.orders.submit_registered(order)
        """
        self._require_session()
        if self.client.options.partner_id and not order.partner_id:
            order.partner_id = self.client.options.partner_id
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/order/submit",
            content=order.to_xml(encoding="unicode", skip_empty=True),
        )
        response = await self.client.request(request)

        # If reviewable=true and 200 OK, order was validated but not created
        if order.reviewable and response.status_code == 200:
            return order

        # If reviewable=false and 201 Created, retrieve order from Location header
        if response.status_code == 201:
            location = response.headers.get("Location", "")
            # Extract order ID from Location URL (e.g., /commerce/order/BBY01-123456789)
            order_id = location.rstrip("/").split("/")[-1]
            if order_id:
                return await self.lookup(order_id)

        return order

    async def review(
        self, order: OrderSubmitRegisteredRequest | OrderSubmitGuestRequest
    ) -> OrderResponse:
        """Review an order and get accurate tax calculations before submitting.

        Always use this endpoint before submitting an order to get the
        most accurate tax calculation. Set reviewable="true" in the order.

        Args:
            order: The order details to review (registered or guest order).
                Should have reviewable="true".

        Returns:
            OrderResponse containing the order with calculated taxes
            and validated item information.

        Raises:
            SessionRequiredError: If not logged in.

        Note:
            This is the recommended method for accurate tax calculations.
            The deprecated /commerce/tax endpoint should not be used.
        """
        self._require_session()
        if self.client.options.partner_id and not order.partner_id:
            order.partner_id = self.client.options.partner_id
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/order/review",
            content=order.to_xml(encoding="unicode", skip_empty=True),
        )
        response = await self.client.request(request)
        return OrderResponse.from_xml(response.text)

    async def submit_guest(
        self, order: OrderSubmitGuestRequest
    ) -> OrderResponse | OrderSubmitGuestRequest:
        """Submit a Guest Order.

        Places an order that will be charged to the customer's credit card.
        No session is required. The credit card information must be encrypted
        using the public key from get_encryption_key().

        Args:
            order: The order details including items, fulfillment options,
                and encrypted payment information.

        Returns:
            If reviewable=False (default) and a session is active: Returns
                OrderResponse with full order details retrieved from the API.
            If reviewable=False but no session: Returns the input order unchanged
                (order was created but details cannot be retrieved without session).
            If reviewable=True: Returns the input order unchanged (order was
                validated but not created).

        Note:
            Use client.encryption.get_encryption_key() to obtain the
            public key for encrypting credit card data. Retrieving order
            details after submission requires an active session.
        """
        if self.client.options.partner_id and not order.partner_id:
            order.partner_id = self.client.options.partner_id
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/guestuser",
            content=order.to_xml(encoding="unicode", skip_empty=True),
        )
        response = await self.client.request(request)

        # If reviewable=true and 200 OK, order was validated but not created
        if order.reviewable and response.status_code == 200:
            return order

        # If reviewable=false and 201 Created, retrieve order from Location header
        if response.status_code == 201:
            location = response.headers.get("Location", "")
            # Extract order ID from Location URL (e.g., /commerce/order/BBY01-123456789)
            order_id = location.rstrip("/").split("/")[-1]
            # Only retrieve if we have a session and an order ID
            if order_id and "X-SESSION-ID" in self.client.client.headers:
                return await self.lookup(order_id)

        return order

    async def query(
        self, order_id: str, last_name: str, phone_number: str
    ) -> OrderResponse:
        """Look up an order by ID, last name, and phone number.

        Allows customers to check their order status without authentication.
        All three parameters must match the original order.

        Args:
            order_id: The Best Buy order ID.
            last_name: Customer's last name from the order.
            phone_number: Customer's phone number from the order.

        Returns:
            OrderResponse containing the order details and status.
        """
        query = OrderQueryRequest(
            order_id=order_id, last_name=last_name, phone_number=phone_number
        )
        request = self.client.client.build_request(
            method="POST",
            url="/commerce/order/query",
            content=query.to_xml(encoding="unicode"),
        )
        response = await self.client.request(request)
        return OrderResponse.from_xml(response.text)

    async def lookup(self, order_id: str) -> OrderResponse:
        """Look up an order by Best Buy order ID.

        Retrieves order details for a Registered Order. Requires an
        active session.

        Args:
            order_id: The Best Buy order ID returned when the order
                was submitted.

        Returns:
            OrderResponse containing the order details and status.

        Raises:
            SessionRequiredError: If not logged in.
        """
        self._require_session()
        request = self.client.client.build_request(
            method="GET",
            url=f"/commerce/order/{order_id}",
        )
        response = await self.client.request(request)
        return OrderResponse.from_xml(response.text)


class EncryptionOperations(CommerceOperations):
    """Operations for retrieving encryption keys for guest orders.

    Guest Orders require credit card information to be encrypted using
    RSA/OAEP encryption with the public key provided by this endpoint.
    """

    def get_encryption_key(self) -> PublicKeyEncryptionResponse:
        """Get the public encryption key for guest order payments.

        Retrieves the RSA public key used to encrypt credit card information
        for Guest Orders. The key should be used with OAEP padding.

        Returns:
            PublicKeyEncryptionResponse containing the public key and
            key identifier to include with the encrypted payment data.

        Example:
            key_response = client.encryption.get_encryption_key()
            # Use key_response.public_key to encrypt credit card data
            # Include key_response.key_id in the order tender
        """
        request = self.client.client.build_request(
            method="GET",
            url="/commerce/encryptionkey",
        )
        response = self.client.request(request)
        return PublicKeyEncryptionResponse.from_xml(response.text)


class AsyncEncryptionOperations(CommerceOperations):
    """Async operations for retrieving encryption keys for guest orders.

    Guest Orders require credit card information to be encrypted using
    RSA/OAEP encryption with the public key provided by this endpoint.
    """

    async def get_encryption_key(self) -> PublicKeyEncryptionResponse:
        """Get the public encryption key for guest order payments.

        Retrieves the RSA public key used to encrypt credit card information
        for Guest Orders. The key should be used with OAEP padding.

        Returns:
            PublicKeyEncryptionResponse containing the public key and
            key identifier to include with the encrypted payment data.

        Example:
            key_response = await client.encryption.get_encryption_key()
            # Use key_response.public_key to encrypt credit card data
            # Include key_response.key_id in the order tender
        """
        request = self.client.client.build_request(
            method="GET",
            url="/commerce/encryptionkey",
        )
        response = await self.client.request(request)
        return PublicKeyEncryptionResponse.from_xml(response.text)
