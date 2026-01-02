from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from pydantic_xml import BaseXmlModel, element, attr, wrapped


class OrderStatus(str, Enum):
    AWAITING_RETURN_PICKUP = "Awaiting Return Pickup"
    AWAITING_SCHEDULING = "Awaiting Scheduling"
    BACKORDERED = "Backordered"
    CANCELED = "Canceled"
    COMPLETED = "Completed"
    DELAYED = "Delayed"
    DELIVERED = "Delivered"
    IN_PROGRESS = "In Progress"
    INCOMPLETE = "Incomplete"
    ITEM_RETURNED = "Item Returned"
    ORDER_RECEIVED = "Order Received"
    OUT_FOR_DELIVERY = "Out for Delivery"
    OUT_OF_STOCK = "Out of Stock"
    PENDING_CANCELLATION = "Pending Cancellation"
    PICKED_UP = "Picked Up"
    PRE_ORDERED = "Pre-Ordered"
    PREPARING = "Preparing"
    READY_TO_PICK_UP = "Ready to Pick Up"
    REFUND_PENDING = "Refund Pending"
    RESCHEDULE_REQUIRED = "Reschedule Required"
    RETURN_IN_TRANSIT = "Return In Transit"
    RETURN_RECEIVED = "Return Received"
    RETURN_REQUEST_CONFIRMED = "Return Request Confirmed"
    RETURNED = "Returned"
    SCHEDULED = "Scheduled"
    SCHEDULING_NEEDED = "Scheduling Needed"
    SHIPPED = "Shipped"


class DeliveryOption(BaseXmlModel, tag="option"):
    delivery_date: date = attr(name="date")
    start_time: str = attr(name="start-time")
    end_time: str = attr(name="end-time")


class DeliveryOptionsResponse(BaseXmlModel, tag="delivery-options"):
    options: List[DeliveryOption] = element(tag="option", default_factory=list)


class DeliveryService(BaseXmlModel, tag="delivery-service"):
    service_type: str = element(tag="service-type")
    delivery_service_id: str = element(tag="delivery-service-id")
    service_display_name: str = element(tag="service-display-name")
    service_long_description: str = element(tag="service-long-description")
    price: Decimal = element(tag="price")


class DeliveryServicesResponse(BaseXmlModel, tag="delivery-services"):
    sku: str = element(tag="sku")
    zipcode: str = element(tag="zipcode")
    delivery_services: List[DeliveryService] = element(
        tag="delivery-service", default_factory=list
    )


class DeliveryDateQueryItem(BaseXmlModel, tag="item"):
    sku_id: str = attr(name="sku-id")


class DeliveryDateQuery(BaseXmlModel, tag="deliverydate-query"):
    item: DeliveryDateQueryItem = element(tag="item")
    zipcode: str = element(tag="zipcode")


class DeliveryDateResponse(BaseXmlModel, tag="deliverydate-response"):
    delivery_dates: List[date] = element(tag="deliverydate", default_factory=list)


class AvailabilityQueryRequest(BaseXmlModel, tag="availability-query"):
    sku_id: str = element(tag="sku-id")


class AvailabilityQueryResponse(BaseXmlModel, tag="availability-query"):
    sku_id: str = attr(name="sku-id")
    order_code: int = element(tag="order-code")
    display_message: str = element(tag="display-message")
    home_delivery_code: int = element(tag="home-delivery-code")
    home_delivery_message: str = element(tag="home-delivery-message")
    instore_availability: bool = element(tag="instore-availability")
    max_quantity: int = element(tag="max-quantity")
    available_for_shipping: Optional[bool] = element(
        tag="available-for-shipping", default=None
    )
    available_for_delivery: Optional[bool] = element(
        tag="available-for-delivery", default=None
    )
    available_for_pickup: Optional[bool] = element(
        tag="available-for-pickup", default=None
    )


class ShippingAddress(BaseXmlModel, tag="address"):
    address1: str = element(tag="address1")
    address2: Optional[str] = element(tag="address2", default="")
    city: str = element(tag="city")
    state: str = element(tag="state")
    postalcode: str = element(tag="postalcode")
    country: str = element(tag="country", default="US")


class ShippingQueryItem(BaseXmlModel, tag="item"):
    sku: str = attr(name="sku")


class ShippingQueryRequest(BaseXmlModel, tag="shipping-query"):
    address: ShippingAddress = element(tag="address")
    item: ShippingQueryItem = element(tag="item")


class ShippingOption(BaseXmlModel, tag="option"):
    price: Decimal = attr(name="price")
    currency: str = attr(name="currency")
    expected_delivery_date: date = attr(name="expected-delivery-date")
    key: str = attr(name="key")
    name: str  # Text content of the element


class ShippingOptionsResponse(BaseXmlModel, tag="shipping-options"):
    sku_id: str = attr(name="sku-id")
    free_shipping: bool = attr(name="free-shipping")
    options: List[ShippingOption] = element(tag="option", default_factory=list)


class PriceQueryRequest(BaseXmlModel, tag="price-query"):
    sku_id: str = element(tag="sku-id")


class UnitPrice(BaseXmlModel, tag="unit-price"):
    sku_id: Optional[str] = attr(name="sku-id", default=None)
    currency: str = attr(name="currency")
    value: Decimal  # Text content of the element


class PriceResponse(BaseXmlModel, tag="price-response"):
    unit_price: UnitPrice = element(tag="unit-price")


class EstimateTaxQuery(BaseXmlModel, tag="estimate-tax"):
    sku_id: str = element(tag="sku-id")
    zipcode: str = element(tag="zipcode")
    shipping_option: Optional[str] = element(tag="shipping-option", default=None)


class EstimatedTax(BaseXmlModel, tag="estimated-tax"):
    sku_id: str = attr(name="sku-id")
    currency: str = attr(name="currency")
    value: Decimal = element(tag="value")


class StoreQuery(BaseXmlModel, tag="store-query"):
    skuid: str = element(tag="skuid")
    zipcode: str = element(tag="zipcode")
    storecount: Optional[int] = element(tag="storecount", default=None)


class Store(BaseXmlModel, tag="store"):
    id: str = attr(name="id")
    name: str = attr(name="name")
    availability_msg: str = attr(name="availabilityMsg")
    href: str = attr(name="href")
    ship_to_store: Optional[bool] = attr(name="ship-to-store", default=None)
    service_level: Optional[str] = attr(name="service-level", default=None)


class Link(BaseXmlModel, tag="link"):
    rel: str = attr(name="rel")
    href: str = attr(name="href")


class StoresResponse(BaseXmlModel, tag="stores"):
    total_count: int = attr(name="totalCount")
    stores: List[Store] = element(tag="store", default_factory=list)
    next_link: Optional[Link] = element(tag="link", default=None)


class ProductServiceRequest(BaseXmlModel, tag="productservice-request"):
    skuid: str = element(tag="skuid")
    zipcode: str = element(tag="zipcode")


class AvailabilityQuery(BaseXmlModel, tag="availability-query"):
    sku_id: str = attr(name="sku-id")
    order_code: int = element(tag="order-code")
    display_message: str = element(tag="display-message")
    home_delivery_code: int = element(tag="home-delivery-code")
    home_delivery_message: str = element(tag="home-delivery-message")
    instore_availability: bool = element(tag="instore-availability")
    max_quantity: int = element(tag="max-quantity")


class ProductServiceResponse(BaseXmlModel, tag="productservice-response"):
    availability_query: Optional[AvailabilityQuery] = element(
        tag="availability-query", default=None
    )
    price_response: Optional[PriceResponse] = element(
        tag="price-response", default=None
    )
    estimated_tax: Optional[EstimatedTax] = element(tag="estimated-tax", default=None)
    shipping_options: Optional[ShippingOptionsResponse] = element(
        tag="shipping-options", default=None
    )
    deliverydate_response: Optional[DeliveryDateResponse] = element(
        tag="deliverydate-response", default=None
    )
    stores: Optional[StoresResponse] = element(tag="stores", default=None)


class Cost(BaseXmlModel, tag="cost"):
    currency: str = attr(name="currency")
    value: Decimal


class TaxCost(BaseXmlModel, tag="tax-cost"):
    currency: str = attr(name="currency")
    value: Optional[Decimal] = None  # Can be empty


class ShippingCost(BaseXmlModel, tag="shipping-cost"):
    currency: str = attr(name="currency")
    fulfillment_id: Optional[str] = attr(name="fulfillment-id", default=None)
    value: Decimal


class OrderItem(BaseXmlModel, tag="item"):
    id: str = attr(name="id")
    quantity: Optional[int] = element(tag="quantity", default=None)
    link: Optional[Link] = element(tag="link", default=None)
    sku: Optional[str] = attr(name="sku", default=None)
    backordered: Optional[bool] = attr(name="backordered", default=None)
    description: Optional[str] = element(tag="description", default=None)
    unit_price: Optional[UnitPrice] = element(tag="unit-price", default=None)
    cost: Optional[Cost] = element(tag="cost", default=None)
    tax_cost: Optional[TaxCost] = element(tag="tax-cost", default=None)
    shipping_cost: Optional[ShippingCost] = element(tag="shipping-cost", default=None)


class OrderList(BaseXmlModel, tag="list"):
    id: Optional[str] = attr(name="id", default=None)
    lastmodified: Optional[str] = attr(name="lastmodified", default=None)
    items: List[OrderItem] = wrapped("items", element(tag="item", default_factory=list))


class OrderAddress(BaseXmlModel, tag="address"):
    type: str = attr(name="type")
    verified: Optional[bool] = attr(name="verified", default=None)
    firstname: str = element(tag="firstname")
    middlename: Optional[str] = element(tag="middlename", default="")
    lastname: str = element(tag="lastname")
    address1: str = element(tag="address1")
    address2: Optional[str] = element(tag="address2", default="")
    city: str = element(tag="city")
    state: str = element(tag="state")
    country: Optional[str] = element(tag="country", default=None)
    postalcode: str = element(tag="postalcode")
    phonenumber: Optional[str] = element(tag="phonenumber", default=None)
    email: Optional[str] = element(tag="email", default=None)
    otherphone: Optional[str] = element(tag="otherphone", default=None)
    fulfillment_id: Optional[str] = attr(name="fulfillment-id", default=None)
    tender_id: Optional[str] = attr(name="tender-id", default=None)


class Shipping(BaseXmlModel, tag="shipping"):
    option: str = attr(name="option")


class AddressFulfillment(BaseXmlModel, tag="address-fulfillment"):
    list: Optional[str] = attr(name="list", default=None)
    item_id: str = attr(name="item-id")
    shipping: Optional[Shipping] = element(tag="shipping", default=None)
    address: Optional[OrderAddress] = element(tag="address", default=None)
    id: Optional[str] = attr(name="id", default=None)
    estimated_shipping_date: Optional[date] = attr(
        name="estimated-shipping-date", default=None
    )


class FriendsFamilyDetails(BaseXmlModel, tag="friends-family-details"):
    firstname: str = element(tag="firstname")
    lastname: str = element(tag="lastname")
    emailaddress: str = element(tag="emailaddress")
    phonenumber: str = element(tag="phonenumber")


class StoreFulfillment(BaseXmlModel, tag="store-fulfillment"):
    store_id: str = attr(name="store-id")
    list: str = attr(name="list")
    item_id: str = attr(name="item-id")
    ship_to_store: Optional[bool] = attr(name="ship-to-store", default=None)
    service_level: Optional[str] = attr(name="service-level", default=None)
    friends_family_details: Optional[FriendsFamilyDetails] = element(
        tag="friends-family-details", default=None
    )


class HomeDeliveryFulfillment(BaseXmlModel, tag="homedelivery-fulfillment"):
    delivery_date: date = attr(name="delivery-date")
    delivery_start_time: str = attr(name="delivery-start-time")
    list: str = attr(name="list")
    item_id: str = attr(name="item-id")
    address: Optional[OrderAddress] = element(tag="address", default=None)


class Fulfillment(BaseXmlModel, tag="fulfillment"):
    address_fulfillment: Optional[AddressFulfillment] = element(
        tag="address-fulfillment", default=None
    )
    store_fulfillment: Optional[StoreFulfillment] = element(
        tag="store-fulfillment", default=None
    )
    homedelivery_fulfillment: Optional[HomeDeliveryFulfillment] = element(
        tag="homedelivery-fulfillment", default=None
    )


class CreditCard(BaseXmlModel, tag="credit-card"):
    """Credit card details used in API responses."""

    cc_number: str = element(tag="cc-number")
    exp_month: str = element(tag="exp-month")
    exp_year: str = element(tag="exp-year")
    cid: str = element(tag="cid")
    address: Optional[OrderAddress] = element(tag="address", default=None)


class CCTender(BaseXmlModel, tag="cc-tender"):
    """Credit card tender used in API responses."""

    cid: Optional[str] = attr(name="cid", default=None)
    last_four: Optional[str] = attr(name="last-four", default=None)
    name: Optional[str] = attr(name="name", default=None)
    id: Optional[str] = attr(name="id", default=None)
    exp_date: Optional[str] = attr(name="exp-date", default=None)
    credit_card: Optional[CreditCard] = element(tag="credit-card", default=None)


class Tender(BaseXmlModel, tag="tender"):
    """Tender used in API responses."""

    purchase_order_number: Optional[str] = element(
        tag="purchase-order-number", default=None
    )
    cc_tender: Optional[CCTender] = element(tag="cc-tender", default=None)


# Registered Order Tender Models


class RegisteredCCTender(BaseXmlModel, tag="cc-tender"):
    """Credit card tender for registered orders.

    For registered orders, the credit card is stored in the Billing Account,
    so only the CID (CVV) is required, or a list reference when using a
    purchase order number.

    Examples:
        Simple form with CID only:
            <cc-tender cid="999"/>

        With purchase order number and list reference:
            <cc-tender list="123"/>
    """

    cid: Optional[str] = attr(name="cid", default=None)
    list: Optional[str] = attr(name="list", default=None)


class RegisteredTender(BaseXmlModel, tag="tender"):
    """Tender for registered orders.

    Registered orders are charged to the company's credit card stored in the
    Billing Account. Only the CID (CVV) is required, or a purchase order number
    with list reference.

    Examples:
        With CID only:
            <tender>
                <cc-tender cid="999"/>
            </tender>

        With purchase order number:
            <tender>
                <purchase-order-number>MSC1277362</purchase-order-number>
                <cc-tender list="123"/>
            </tender>
    """

    purchase_order_number: Optional[str] = element(
        tag="purchase-order-number", default=None
    )
    cc_tender: RegisteredCCTender = element(tag="cc-tender")


# Guest Order Tender Models


class BillingAddress(BaseXmlModel, tag="address"):
    """Billing address for guest order credit card.

    The billing address is required for guest orders and must have
    type="billing".
    """

    type: str = attr(name="type", default="billing")
    verified: bool = attr(name="verified", default=False)
    firstname: str = element(tag="firstname")
    middlename: Optional[str] = element(tag="middlename", default=None)
    lastname: str = element(tag="lastname")
    address1: str = element(tag="address1")
    address2: Optional[str] = element(tag="address2", default=None)
    city: str = element(tag="city")
    state: str = element(tag="state")
    postalcode: str = element(tag="postalcode")
    country: str = element(tag="country", default="US")
    phonenumber: str = element(tag="phonenumber")
    email: str = element(tag="email")
    otherphone: Optional[str] = element(tag="otherphone", default=None)


class GuestCreditCard(BaseXmlModel, tag="credit-card"):
    """Credit card details for guest orders.

    Guest orders require an encrypted payment token in cc_number, obtained
    by encrypting the credit card number with the public key from
    /commerce/encryptionkey.

    The exp_month, exp_year, and cid fields are optional when using an
    encrypted payment token that includes this information.
    """

    cc_number: str = element(tag="cc-number")
    exp_month: Optional[str] = element(tag="exp-month", default=None)
    exp_year: Optional[str] = element(tag="exp-year", default=None)
    cid: Optional[str] = element(tag="cid", default=None)
    address: BillingAddress = element(tag="address")


class GuestCCTender(BaseXmlModel, tag="cc-tender"):
    """Credit card tender for guest orders.

    Contains the encrypted credit card details for charging the customer's
    credit card.
    """

    credit_card: GuestCreditCard = element(tag="credit-card")


class GuestTender(BaseXmlModel, tag="tender"):
    """Tender for guest orders.

    Guest orders are charged to the customer's credit card, which must be
    encrypted using the public key from /commerce/encryptionkey.

    Examples:
        Basic guest tender:
            <tender>
                <cc-tender>
                    <credit-card>
                        <cc-number>Encrypted Payment Token</cc-number>
                        <exp-month>12</exp-month>
                        <exp-year>2025</exp-year>
                        <cid>999</cid>
                        <address type="billing" verified="false">...</address>
                    </credit-card>
                </cc-tender>
            </tender>

        With purchase order number:
            <tender>
                <purchase-order-number>MSC1277362</purchase-order-number>
                <cc-tender>
                    <credit-card>...</credit-card>
                </cc-tender>
            </tender>
    """

    purchase_order_number: Optional[str] = element(
        tag="purchase-order-number", default=None
    )
    cc_tender: GuestCCTender = element(tag="cc-tender")


class CartTotal(BaseXmlModel, tag="total"):
    currency: str = attr(name="currency")
    product_cost: Decimal = element(tag="product-cost")
    sales_tax: Decimal = element(tag="sales-tax")
    order_cost: Decimal = element(tag="order-cost")
    shipping_cost: Decimal = element(tag="shipping-cost")


class Cart(BaseXmlModel, tag="cart"):
    items: List[OrderItem] = wrapped("items", element(tag="item", default_factory=list))
    total: CartTotal = element(tag="total")


class OrderQueryRequest(BaseXmlModel, tag="order-query"):
    order_id: str = element(tag="order-id")
    last_name: str = element(tag="last-name")
    phone_number: str = element(tag="phone-number")


class OrderSubmitRegisteredRequest(BaseXmlModel, tag="order"):
    """Request to submit a registered order.

    Registered orders are charged to the company's credit card stored in the
    Billing Account. Requires authentication via login.
    """

    id: str = attr(name="id")
    partner_id: Optional[str] = attr(name="partner-id", default=None)
    reviewable: bool = attr(name="reviewable", default=False)
    order_list: OrderList = element(tag="list")
    fulfillment: Fulfillment = element(tag="fulfillment")
    tender: RegisteredTender = element(tag="tender")


class OrderSubmitGuestRequest(BaseXmlModel, tag="order"):
    """Request to submit a guest order.

    Guest orders are charged to the customer's credit card, which must be
    encrypted using the public key from /commerce/encryptionkey.
    """

    id: str = attr(name="id")
    partner_id: Optional[str] = attr(name="partner-id", default=None)
    reviewable: bool = attr(name="reviewable", default=False)
    order_list: OrderList = element(tag="list")
    fulfillment: Fulfillment = element(tag="fulfillment")
    tender: GuestTender = element(tag="tender")


class OrderResponse(BaseXmlModel, tag="order"):
    id: Optional[str] = attr(name="id", default=None)
    reviewable: Optional[bool] = attr(name="reviewable", default=None)
    partner_id: Optional[str] = attr(name="partner-id", default=None)
    status: Optional[OrderStatus] = attr(name="status", default=None)
    order_date: Optional[date] = attr(name="order-date", default=None)
    total: Optional[Decimal] = attr(name="total", default=None)
    given_id: Optional[str] = attr(name="given-id", default=None)
    link: Optional[Link] = element(tag="link", default=None)
    order_list: Optional[OrderList] = element(tag="list", default=None)
    fulfillment: Optional[Fulfillment] = element(tag="fulfillment", default=None)
    tender: Optional[Tender] = element(tag="tender", default=None)
    cart: Optional[Cart] = element(tag="cart", default=None)
    addresses: Optional[List[OrderAddress]] = wrapped(
        "addresses", element(tag="address", default_factory=list)
    )


class IdMapEntry(BaseXmlModel, tag="entry"):
    key: str = element(tag="key")
    value: str = element(tag="value")


class OrderSubmitResponse(BaseXmlModel, tag="order-response"):
    version: str = attr(name="version")
    status: str = attr(name="status")
    link: Optional[Link] = element(tag="link", default=None)
    id_map: Optional[List[IdMapEntry]] = wrapped(
        "id-map", element(tag="entry", default_factory=list)
    )
    messages: Optional[str] = element(tag="messages", default=None)


class PublicKeyEncryptionResponse(BaseXmlModel, tag="publicKeyEncryption"):
    terminal_id: str = element(tag="terminalId")
    track_id: str = element(tag="trackId")
    key_id: str = element(tag="keyId")
    base64_encoded_public_key_bytes: str = element(tag="base64EncodedPublicKeyBytes")


class CommerceResponse(BaseXmlModel, tag="commerce"):
    version: str = attr(name="version")
    links: List[Link] = element(tag="link", default_factory=list)


# Error Models


class ApiErrorMessage(BaseXmlModel, tag="message"):
    text: str
    sku: Optional[str] = attr(name="sku", default=None)


class ApiError(BaseXmlModel, tag="error"):
    code: Optional[str] = attr(name="code", default=None)
    message: ApiErrorMessage = element(tag="message")


class ApiErrors(BaseXmlModel, tag="errors"):
    errors: List[ApiError] = element(tag="error", default_factory=list)


class SimpleError(BaseXmlModel, tag="Error"):
    message: str = element(tag="Message")
