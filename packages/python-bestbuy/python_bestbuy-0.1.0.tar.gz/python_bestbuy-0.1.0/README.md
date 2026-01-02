# python-bestbuy

[![CI](https://github.com/bbify/python-bestbuy/actions/workflows/ci.yml/badge.svg)](https://github.com/bbify/python-bestbuy/actions/workflows/ci.yml)

A Python client library for Best Buy's APIs, providing synchronous and asynchronous HTTP clients for interacting with Best Buy's Catalog and Commerce services.

## Features

- **Dual API Support**: Full support for both the Catalog API (product information, categories, stores, recommendations) and Commerce API (orders, fulfillment, pricing)
- **Sync and Async Clients**: Both synchronous and asynchronous clients for each API
- **Automatic Pagination**: Built-in paginators for iterating over large result sets
- **Type Safety**: Full Pydantic model validation for requests and responses
- **Session Management**: Automatic session handling for Commerce API authentication
- **Payment Encryption**: Built-in utilities for encrypting credit card data for guest orders
- **Sandbox Support**: Easy switching between production and sandbox environments

## Installation

```bash
pip install python-bestbuy
```

Or using uv:

```bash
uv add python-bestbuy
```

### Requirements

- Python 3.10+
- httpx
- pydantic-xml
- cryptography

## Usage

### Catalog API

The Catalog API provides access to Best Buy's product catalog, categories, store locations, and product recommendations.

```python
from bestbuy.clients.catalog import CatalogClient, AsyncCatalogClient

# Initialize the client
client = CatalogClient(api_key="your-api-key")
```

#### Products

```python
# Get a single product by SKU
product = client.products.get(sku=6487435)
print(f"{product.name}: ${product.sale_price}")

# Get specific attributes only
product = client.products.get(sku=6487435, show=["name", "salePrice", "manufacturer"])

# Search for products
results = client.products.search(
    query="manufacturer=apple&salePrice<1000",
    show=["sku", "name", "salePrice"],
    sort="salePrice",
    sort_order="asc",
    page=1,
    page_size=10
)
for product in results.products:
    print(f"{product.sku}: {product.name}")

# List all products
results = client.products.list(page=1, page_size=10)

# Get warranties for a product
warranties = client.products.get_warranties(sku=6487435)

# Paginate through search results
for page in client.products.search_pages(query="onSale=true", page_size=100):
    for product in page.products:
        print(product.name)

# Iterate over individual products across all pages
for product in client.products.search_pages(query="onSale=true").items():
    print(product.name)

# Limit pagination to a maximum number of pages
for product in client.products.search_pages(query="onSale=true", max_pages=5).items():
    print(product.name)
```

#### Categories

```python
# Get a single category
category = client.categories.get(category_id="abcat0100000")
print(f"{category.name}: {category.id}")

# Search for categories
results = client.categories.search(query="name=Laptops*")
for category in results.categories:
    print(category.name)

# List all categories
results = client.categories.list(page=1, page_size=10)

# Paginate through categories
for category in client.categories.search_pages().items():
    print(category.name)
```

#### Stores

```python
# Get a single store by ID
store = client.stores.get(store_id=281)
print(f"{store.name}: {store.city}, {store.region}")

# Search for stores
results = client.stores.search(query="city=Minneapolis")
for store in results.stores:
    print(f"{store.store_id}: {store.name}")

# List all stores
results = client.stores.list(page=1, page_size=10)

# Find stores near a ZIP code
results = client.stores.search_by_area(postal_code="55401", distance=25)
for store in results.stores:
    print(f"{store.name} - {store.distance} miles")

# Find stores near coordinates
results = client.stores.search_by_area(lat=44.9778, lng=-93.2650, distance=10)

# Paginate through stores by area
for store in client.stores.search_by_area_pages(postal_code="55401").items():
    print(store.name)
```

#### Recommendations

```python
# Get trending products
trending = client.recommendations.trending()
for product in trending.results:
    print(f"Trending: {product.name}")

# Get trending products in a specific category
trending = client.recommendations.trending(category_id="abcat0502000")

# Get most viewed products
most_viewed = client.recommendations.most_viewed()
for product in most_viewed.results:
    print(f"Most viewed: {product.name}")

# Get products also viewed with a specific product
also_viewed = client.recommendations.also_viewed(sku=6487435)
for product in also_viewed.results:
    print(f"Also viewed: {product.name}")

# Get products also bought with a specific product
also_bought = client.recommendations.also_bought(sku=6487435)

# Get products ultimately bought after viewing a product
ultimately_bought = client.recommendations.viewed_ultimately_bought(sku=6487435)
```

#### Async Catalog Client

```python
import asyncio
from bestbuy.clients.catalog import AsyncCatalogClient

async def main():
    client = AsyncCatalogClient(api_key="your-api-key")

    # All operations are async
    product = await client.products.get(sku=6487435)
    print(product.name)

    # Async pagination
    async for product in client.products.search_pages(query="onSale=true").items():
        print(product.name)

asyncio.run(main())
```

### Commerce API

The Commerce API provides access to Best Buy's order management, fulfillment options, pricing, and payment services.

```python
from bestbuy.clients.commerce import CommerceClient, AsyncCommerceClient

# Initialize the client (sandbox mode by default)
client = CommerceClient(
    api_key="your-api-key",
    username="your-username",  # For registered orders
    password="your-password",
    sandbox=True  # Use sandbox environment
)

# Production mode
client = CommerceClient(
    api_key="your-api-key",
    sandbox=False
)
```

#### Authentication

Authentication is required for registered orders (orders charged to your company credit card).

```python
# Using context manager (recommended)
with client.auth:
    # Session is automatically managed
    response = client.orders.submit_registered(order)
# Session is automatically logged out

# With explicit credentials
with client.auth(username="user", password="pass"):
    response = client.orders.submit_registered(order)

# Manual login/logout
client.auth.login()
try:
    response = client.orders.submit_registered(order)
finally:
    client.auth.logout()
```

#### Fulfillment Operations

```python
# Check product availability
availability = client.fulfillment.check_availability(sku="5628900")
print(f"Shipping available: {availability.available_for_shipping}")
print(f"Pickup available: {availability.available_for_pickup}")
print(f"Delivery available: {availability.available_for_delivery}")
print(f"Max quantity: {availability.max_quantity}")

# Get shipping options
shipping = client.fulfillment.get_shipping_options(
    sku="5628900",
    address1="123 Main St",
    city="Minneapolis",
    state="MN",
    postalcode="55401"
)
for option in shipping.options:
    print(f"{option.name}: ${option.price} - Delivery by {option.expected_delivery_date}")

# Find stores with product availability
stores = client.fulfillment.find_stores(
    sku="5628900",
    zip_code="55401",
    store_count=5
)
for store in stores.stores:
    print(f"{store.name}: {store.availability_msg}")

# Get home delivery options (for large items)
delivery_options = client.fulfillment.get_delivery_options(
    sku="5628900",
    zip_code="55401"
)
for option in delivery_options.options:
    print(f"{option.delivery_date}: {option.start_time} - {option.end_time}")

# Get delivery services (installation, haul away, etc.)
services = client.fulfillment.get_delivery_services(
    sku="5628900",
    zip_code="55401"
)
for service in services.delivery_services:
    print(f"{service.service_display_name}: ${service.price}")
```

#### Pricing Operations

```python
# Get unit price for a SKU
price = client.pricing.get_unit_price(sku="5628900")
print(f"Price: ${price.unit_price.value}")

# Get combined product service info (availability, price, shipping, stores)
product_info = client.pricing.get_product_service(
    sku="5628900",
    zip_code="55401"
)
```

#### Order Operations

```python
from bestbuy.models.commerce import (
    OrderSubmitRegisteredRequest,
    OrderSubmitGuestRequest,
    OrderList,
    OrderItem,
    Fulfillment,
    AddressFulfillment,
    ShippingAddress,
    Tender,
)

# Create a registered order (requires authentication)
order = OrderSubmitRegisteredRequest(
    id="my-order-123",
    order_list=OrderList(
        id="list-1",
        items=[
            OrderItem(
                id="item-1",
                quantity=1,
                sku="5628900"
            )
        ]
    ),
    fulfillment=Fulfillment(
        address_fulfillment=AddressFulfillment(
            address=ShippingAddress(
                address1="123 Main St",
                city="Minneapolis",
                state="MN",
                postalcode="55401"
            ),
            shipping_option_key="1"  # From get_shipping_options
        )
    ),
    tender=Tender()
)

# Review order (get accurate tax calculation)
with client.auth:
    review_response = client.orders.review(order)
    print(f"Total: ${review_response.total}")

    # Submit the order
    submit_response = client.orders.submit_registered(order)
    print(f"Order ID: {submit_response.id_map}")

# Query an existing order (no auth required)
order_details = client.orders.query(
    order_id="BBY01-123456789",
    last_name="Smith",
    phone_number="6125551234"
)
print(f"Status: {order_details.status}")

# Lookup order by ID (requires auth)
with client.auth:
    order_details = client.orders.lookup(order_id="BBY01-123456789")
```

#### Guest Orders

Guest orders are charged to the customer's credit card and require payment encryption.

```python
from bestbuy.utils.encryption import create_encrypted_payment_token

# Get encryption key
encryption_key = client.encryption.get_encryption_key()

# Create encrypted payment token
payment_token = create_encrypted_payment_token(
    card_number="5424180279791773",
    base64_encoded_public_key=encryption_key.base64_encoded_public_key_bytes,
    terminal_id=encryption_key.terminal_id,
    track_id=encryption_key.track_id,
    key_id=encryption_key.key_id
)

# Create guest order with encrypted payment
guest_order = OrderSubmitGuestRequest(
    id="guest-order-123",
    order_list=OrderList(
        id="list-1",
        items=[
            OrderItem(id="item-1", quantity=1, sku="5628900")
        ]
    ),
    fulfillment=Fulfillment(
        address_fulfillment=AddressFulfillment(
            address=ShippingAddress(
                address1="123 Main St",
                city="Minneapolis",
                state="MN",
                postalcode="55401"
            ),
            shipping_option_key="1"
        )
    ),
    tender=Tender(
        # Include encrypted payment token in tender
    )
)

# Submit guest order (no auth required)
response = client.orders.submit_guest(guest_order)
```

#### Encryption Operations

```python
# Get the public encryption key for guest orders
key_response = client.encryption.get_encryption_key()
print(f"Terminal ID: {key_response.terminal_id}")
print(f"Track ID: {key_response.track_id}")
print(f"Key ID: {key_response.key_id}")
```

#### Async Commerce Client

```python
import asyncio
from bestbuy.clients.commerce import AsyncCommerceClient

async def main():
    client = AsyncCommerceClient(
        api_key="your-api-key",
        username="your-username",
        password="your-password"
    )

    # Check availability
    availability = await client.fulfillment.check_availability(sku="5628900")
    print(availability.available_for_shipping)

    # Async authentication context
    async with client.auth:
        response = await client.orders.submit_registered(order)

asyncio.run(main())
```

### Configuration Options

#### Catalog Client Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | str | Required | Best Buy API key |
| `base_url` | str | `https://api.bestbuy.com` | API base URL |
| `timeout_ms` | int | `30000` | Request timeout in milliseconds |
| `log_level` | int | `logging.WARNING` | Logging level |

#### Commerce Client Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_key` | str | Required | Best Buy API key |
| `username` | str | None | Billing account username |
| `password` | str | None | Billing account password |
| `partner_id` | str | None | Partner ID for orders |
| `sandbox` | bool | `True` | Use sandbox environment |
| `auto_logout` | bool | `True` | Auto-logout on session end |
| `base_url` | str | Auto | API base URL (auto-set based on sandbox) |
| `timeout_ms` | int | `30000` | Request timeout in milliseconds |
| `log_level` | int | `logging.WARNING` | Logging level |

### Error Handling

```python
from bestbuy.exceptions import APIError, ConfigError, SessionRequiredError

try:
    product = client.products.get(sku=999999999)
except APIError as e:
    print(f"API Error: {e.message}")
    print(f"Error Code: {e.code}")
    print(f"Response: {e.response_text}")
except ConfigError as e:
    print(f"Configuration Error: {e}")

# Commerce API specific
try:
    client.orders.submit_registered(order)  # Without authentication
except SessionRequiredError as e:
    print("Must be logged in to submit orders")
```

### Sandbox Testing

For the Commerce API, use the sandbox environment for testing:

```python
client = CommerceClient(
    api_key="your-sandbox-api-key",
    sandbox=True  # Default
)

# Test credit card for sandbox
# Card Number: 5424180279791773
# Expiration: 12/2025
# CVV: 999
```

## Development

### Running Tests

```bash
uv run pytest
```

### Running Type Checks

```bash
uv run mypy
```

## License

MIT
