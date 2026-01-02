from datetime import date, datetime
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


# Category Models


class CategoryPathItem(BaseModel):
    """A single item in a category's path hierarchy."""

    id: str
    name: str


class SubCategory(BaseModel):
    """A subcategory reference within a category."""

    id: str
    name: str


class Category(BaseModel):
    """A Best Buy product category."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    active: bool
    url: str
    path: List[CategoryPathItem]
    sub_categories: List[SubCategory] = Field(alias="subCategories")


class CategoriesResponse(BaseModel):
    """Response containing a list of categories with pagination metadata."""

    model_config = ConfigDict(populate_by_name=True)

    # Pagination metadata
    from_: int = Field(alias="from")
    to: int
    current_page: int = Field(alias="currentPage")
    total: int
    total_pages: int = Field(alias="totalPages")
    query_time: str = Field(alias="queryTime")
    total_time: str = Field(alias="totalTime")
    canonical_url: str = Field(alias="canonicalUrl")
    partial: bool = False

    # Categories
    categories: List[Category]


# Product Models


class ProductImage(BaseModel):
    """A product image with metadata."""

    model_config = ConfigDict(populate_by_name=True)

    rel: str
    unit_of_measure: str = Field(alias="unitOfMeasure")
    width: Optional[str] = None
    height: Optional[str] = None
    href: str
    primary: bool


class ProductDetail(BaseModel):
    """A product detail/specification."""

    name: str
    value: str
    values: List[str]


class ProductFeature(BaseModel):
    """A product feature description."""

    feature: str


class IncludedItem(BaseModel):
    """An item included with the product."""

    model_config = ConfigDict(populate_by_name=True)

    included_item: str = Field(alias="includedItem")


class ProductVariation(BaseModel):
    """A variation of a product (e.g., different color)."""

    name: str
    value: str


class ProductVariant(BaseModel):
    """A product variant with its variations."""

    sku: str
    variations: List[ProductVariation] = []


class RequiredPart(BaseModel):
    """A required part for the product."""

    sku: str


class BundledProduct(BaseModel):
    """A product this item is bundled in."""

    sku: Union[int, str]


class AccessorySku(BaseModel):
    """An accessory SKU for a product."""

    sku: int


class MemberSku(BaseModel):
    """A member SKU within a bundle."""

    sku: int


class ProductList(BaseModel):
    """A curated list that includes this product."""

    model_config = ConfigDict(populate_by_name=True)

    list_id: str = Field(alias="listId")
    start_date: Optional[date] = Field(default=None, alias="startDate")
    end_date: Optional[date] = Field(default=None, alias="endDate")


class ShippingInfo(BaseModel):
    """Shipping cost information."""

    model_config = ConfigDict(populate_by_name=True)

    ground: Union[float, int, str] = ""
    second_day: Union[float, int, str] = Field(default="", alias="secondDay")
    next_day: Union[float, int, str] = Field(default="", alias="nextDay")
    vendor_delivery: str = Field(default="", alias="vendorDelivery")


class ShippingLevelOfService(BaseModel):
    """A shipping service level option."""

    model_config = ConfigDict(populate_by_name=True)

    service_level_id: int = Field(alias="serviceLevelId")
    service_level_name: str = Field(alias="serviceLevelName")
    unit_shipping_price: Union[float, int] = Field(alias="unitShippingPrice")


class ContractPrice(BaseModel):
    """Price information for a contract."""

    model_config = ConfigDict(populate_by_name=True)

    current: Union[float, int]
    regular: Union[float, int]
    tax_basis: Union[float, int] = Field(alias="taxBasis")
    bby_down_payment: int = Field(default=0, alias="bbyDownPayment")
    bill_credit_amt: int = Field(default=0, alias="billCreditAmt")
    down_payment_amount: int = Field(default=0, alias="downPaymentAmount")
    number_of_payments: int = Field(default=0, alias="numberOfPayments")


class ContractTerm(BaseModel):
    """Contract term duration."""

    duration: int
    units: str


class Contract(BaseModel):
    """A contract option for the product."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    type: str
    purchase_type: str = Field(alias="purchaseType")
    description: str
    default_contract: bool = Field(alias="defaultContract")
    price_note: Optional[str] = Field(default=None, alias="priceNote")
    prices: List[ContractPrice] = []
    term: List[ContractTerm] = []


class GiftSku(BaseModel):
    """A gift SKU included with an offer."""

    sku: int
    quantity: int


class Offer(BaseModel):
    """A special offer for the product."""

    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    type: str
    heading: Optional[str] = None
    text: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = Field(default=None, alias="imageUrl")
    offer_name: Optional[str] = Field(default=None, alias="offerName")
    start_date: Optional[date] = Field(default=None, alias="startDate")
    end_date: Optional[date] = Field(default=None, alias="endDate")
    content_notes: Optional[str] = Field(default=None, alias="contentNotes")
    gift_sku: List[GiftSku] = Field(default=[], alias="giftSku")


class PlaybackFormat(BaseModel):
    """A supported playback format."""

    format: str


class LanguageOption(BaseModel):
    """A supported language option."""

    language: str


class Product(BaseModel):
    """A Best Buy product."""

    model_config = ConfigDict(populate_by_name=True)

    # Core identifiers
    sku: int
    product_id: Optional[str] = Field(default=None, alias="productId")
    upc: str
    name: str
    model_number: str = Field(alias="modelNumber")
    manufacturer: Optional[str] = None

    # Classification
    type: str
    product_template: str = Field(alias="productTemplate")
    department: str
    department_id: int = Field(alias="departmentId")
    class_: str = Field(alias="class")
    class_id: int = Field(alias="classId")
    subclass: str
    subclass_id: int = Field(alias="subclassId")

    # Categories
    category_path: List[CategoryPathItem] = Field(alias="categoryPath")
    alternate_categories: List[CategoryPathItem] = Field(
        default=[], alias="alternateCategories"
    )

    # Pricing
    regular_price: Union[float, int] = Field(alias="regularPrice")
    sale_price: Union[float, int] = Field(alias="salePrice")
    on_sale: bool = Field(alias="onSale")
    clearance: bool
    dollar_savings: Union[float, int] = Field(alias="dollarSavings")
    percent_savings: str = Field(alias="percentSavings")
    plan_price: Optional[float] = Field(default=None, alias="planPrice")
    price_restriction: Optional[str] = Field(default=None, alias="priceRestriction")
    price_update_date: datetime = Field(alias="priceUpdateDate")

    # Availability
    active: bool
    new: bool
    orderable: str
    start_date: date = Field(alias="startDate")
    active_update_date: datetime = Field(alias="activeUpdateDate")
    in_store_availability: bool = Field(alias="inStoreAvailability")
    in_store_availability_text: Optional[str] = Field(
        default=None, alias="inStoreAvailabilityText"
    )
    in_store_availability_text_html: Optional[str] = Field(
        default=None, alias="inStoreAvailabilityTextHtml"
    )
    in_store_availability_update_date: datetime = Field(
        alias="inStoreAvailabilityUpdateDate"
    )
    online_availability: bool = Field(alias="onlineAvailability")
    online_availability_text: Optional[str] = Field(
        default=None, alias="onlineAvailabilityText"
    )
    online_availability_text_html: Optional[str] = Field(
        default=None, alias="onlineAvailabilityTextHtml"
    )
    online_availability_update_date: datetime = Field(
        alias="onlineAvailabilityUpdateDate"
    )
    release_date: Optional[date] = Field(default=None, alias="releaseDate")
    item_update_date: datetime = Field(alias="itemUpdateDate")
    special_order: bool = Field(alias="specialOrder")

    # Fulfillment
    in_store_pickup: bool = Field(alias="inStorePickup")
    friends_and_family_pickup: bool = Field(alias="friendsAndFamilyPickup")
    home_delivery: bool = Field(alias="homeDelivery")
    free_shipping: Optional[bool] = Field(default=None, alias="freeShipping")
    free_shipping_eligible: bool = Field(alias="freeShippingEligible")
    shipping_cost: Union[float, int, str] = Field(default="", alias="shippingCost")
    shipping: List[ShippingInfo] = []
    shipping_levels_of_service: List[ShippingLevelOfService] = Field(
        default=[], alias="shippingLevelsOfService"
    )
    shipping_weight: Union[float, int] = Field(alias="shippingWeight")
    shipping_restrictions: Optional[str] = Field(
        default=None, alias="shippingRestrictions"
    )
    quantity_limit: Optional[int] = Field(default=None, alias="quantityLimit")
    fulfilled_by: Optional[str] = Field(default=None, alias="fulfilledBy")
    haulaway_available: Optional[bool] = Field(default=None, alias="haulawayAvailable")

    # Descriptions
    short_description: Optional[str] = Field(default=None, alias="shortDescription")
    short_description_html: Optional[str] = Field(
        default=None, alias="shortDescriptionHtml"
    )
    long_description: str = Field(alias="longDescription")
    long_description_html: str = Field(alias="longDescriptionHtml")
    description: Optional[str] = None

    # URLs
    url: str
    mobile_url: str = Field(alias="mobileUrl")
    add_to_cart_url: str = Field(alias="addToCartUrl")
    spin360_url: Optional[str] = Field(default=None, alias="spin360Url")
    affiliate_url: Optional[str] = Field(default=None, alias="affiliateUrl")
    affiliate_add_to_cart_url: Optional[str] = Field(
        default=None, alias="affiliateAddToCartUrl"
    )
    link_share_affiliate_url: str = Field(default="", alias="linkShareAffiliateUrl")
    link_share_affiliate_add_to_cart_url: str = Field(
        default="", alias="linkShareAffiliateAddToCartUrl"
    )

    # Images
    image: Optional[str] = None
    images: List[ProductImage] = []
    large_front_image: Optional[str] = Field(default=None, alias="largeFrontImage")
    medium_image: Optional[str] = Field(default=None, alias="mediumImage")
    thumbnail_image: Optional[str] = Field(default=None, alias="thumbnailImage")
    large_image: Optional[str] = Field(default=None, alias="largeImage")
    alternate_views_image: Optional[str] = Field(
        default=None, alias="alternateViewsImage"
    )
    angle_image: Optional[str] = Field(default=None, alias="angleImage")
    back_view_image: Optional[str] = Field(default=None, alias="backViewImage")
    energy_guide_image: Optional[str] = Field(default=None, alias="energyGuideImage")
    left_view_image: Optional[str] = Field(default=None, alias="leftViewImage")
    accessories_image: Optional[str] = Field(default=None, alias="accessoriesImage")
    remote_control_image: Optional[str] = Field(
        default=None, alias="remoteControlImage"
    )
    right_view_image: Optional[str] = Field(default=None, alias="rightViewImage")
    top_view_image: Optional[str] = Field(default=None, alias="topViewImage")

    # Reviews
    customer_review_count: Optional[int] = Field(
        default=None, alias="customerReviewCount"
    )
    customer_review_average: Optional[Union[float, int]] = Field(
        default=None, alias="customerReviewAverage"
    )
    customer_top_rated: Optional[bool] = Field(default=None, alias="customerTopRated")

    # Product details
    details: List[ProductDetail] = []
    features: List[ProductFeature] = []
    included_item_list: List[IncludedItem] = Field(default=[], alias="includedItemList")

    # Variations and related products
    product_variations: List[ProductVariant] = Field(
        default=[], alias="productVariations"
    )
    required_parts: List[RequiredPart] = Field(default=[], alias="requiredParts")
    bundled_in: List[BundledProduct] = Field(default=[], alias="bundledIn")
    accessories: List[AccessorySku] = []
    related_products: List[str] = Field(default=[], alias="relatedProducts")
    frequently_purchased_with: List[str] = Field(
        default=[], alias="frequentlyPurchasedWith"
    )
    cross_sell: List[str] = Field(default=[], alias="crossSell")
    product_families: List[str] = Field(default=[], alias="productFamilies")
    members: List[MemberSku] = []

    # Contracts and offers
    contracts: List[Contract] = []
    offers: List[Offer] = []
    price_with_plan: List[str] = Field(default=[], alias="priceWithPlan")

    # Protection plans
    protection_plan_term: str = Field(default="", alias="protectionPlanTerm")
    protection_plan_type: Optional[str] = Field(
        default=None, alias="protectionPlanType"
    )
    protection_plan_low_price: str = Field(default="", alias="protectionPlanLowPrice")
    protection_plan_high_price: str = Field(default="", alias="protectionPlanHighPrice")
    protection_plans: List[str] = Field(default=[], alias="protectionPlans")
    protection_plan_details: List[str] = Field(
        default=[], alias="protectionPlanDetails"
    )
    buyback_plans: List[str] = Field(default=[], alias="buybackPlans")
    tech_support_plans: List[str] = Field(default=[], alias="techSupportPlans")

    # Physical attributes
    color: Optional[str] = None
    condition: str
    weight: Optional[str] = None
    height: Optional[str] = None
    width: Optional[str] = None
    depth: Optional[str] = None

    # Warranty
    warranty_labor: Optional[str] = Field(default=None, alias="warrantyLabor")
    warranty_parts: Optional[str] = Field(default=None, alias="warrantyParts")

    # Digital/Preowned
    digital: bool
    preowned: bool

    # Sales ranking
    score: Optional[float] = None
    sales_rank_short_term: Optional[int] = Field(
        default=None, alias="salesRankShortTerm"
    )
    sales_rank_medium_term: Optional[int] = Field(
        default=None, alias="salesRankMediumTerm"
    )
    sales_rank_long_term: Optional[int] = Field(default=None, alias="salesRankLongTerm")
    best_selling_rank: Optional[int] = Field(default=None, alias="bestSellingRank")

    # Carrier/Plan info (for phones)
    carriers: List[str] = []
    carrier_plans: List[str] = Field(default=[], alias="carrierPlans")
    plan_features: List[str] = Field(default=[], alias="planFeatures")
    devices: List[str] = []
    technology_code: Optional[str] = Field(default=None, alias="technologyCode")
    carrier_model_number: Optional[str] = Field(
        default=None, alias="carrierModelNumber"
    )
    early_termination_fees: List[str] = Field(default=[], alias="earlyTerminationFees")
    monthly_recurring_charge: str = Field(default="", alias="monthlyRecurringCharge")
    monthly_recurring_charge_grand_total: str = Field(
        default="", alias="monthlyRecurringChargeGrandTotal"
    )
    activation_charge: str = Field(default="", alias="activationCharge")
    minute_price: str = Field(default="", alias="minutePrice")
    plan_category: Optional[str] = Field(default=None, alias="planCategory")
    plan_type: Optional[str] = Field(default=None, alias="planType")
    family_individual_code: Optional[str] = Field(
        default=None, alias="familyIndividualCode"
    )
    valid_from: Optional[str] = Field(default=None, alias="validFrom")
    valid_until: Optional[str] = Field(default=None, alias="validUntil")
    carrier_plan: Optional[str] = Field(default=None, alias="carrierPlan")

    # Media info (for movies/music)
    format: Optional[str] = None
    album_title: str = Field(default="", alias="albumTitle")
    album_label: Optional[str] = Field(default=None, alias="albumLabel")
    artist_name: Optional[str] = Field(default=None, alias="artistName")
    artist_id: Optional[str] = Field(default=None, alias="artistId")
    original_release_date: Optional[date] = Field(
        default=None, alias="originalReleaseDate"
    )
    parental_advisory: Optional[str] = Field(default=None, alias="parentalAdvisory")
    media_count: Optional[int] = Field(default=None, alias="mediaCount")
    mono_stereo: Optional[str] = Field(default=None, alias="monoStereo")
    studio_live: Optional[str] = Field(default=None, alias="studioLive")
    genre: Optional[str] = None
    discs: List[str] = []
    cast: List[str] = []
    crew: List[str] = []

    # Movie info
    aspect_ratio: Optional[str] = Field(default=None, alias="aspectRatio")
    screen_format: Optional[str] = Field(default=None, alias="screenFormat")
    length_in_minutes: Optional[int] = Field(default=None, alias="lengthInMinutes")
    mpaa_rating: Optional[str] = Field(default=None, alias="mpaaRating")
    plot: Optional[str] = None
    plot_html: Optional[str] = Field(default=None, alias="plotHtml")
    studio: Optional[str] = None
    theatrical_release_date: Optional[date] = Field(
        default=None, alias="theatricalReleaseDate"
    )

    # Software/Games
    software_age: Optional[str] = Field(default=None, alias="softwareAge")
    software_grade: Optional[str] = Field(default=None, alias="softwareGrade")
    platform: Optional[str] = None
    number_of_players: Optional[int] = Field(default=None, alias="numberOfPlayers")
    software_number_of_players: Optional[int] = Field(
        default=None, alias="softwareNumberOfPlayers"
    )
    esrb_rating: Optional[str] = Field(default=None, alias="esrbRating")

    # Misc
    source: Optional[str] = None
    search: Optional[str] = None
    best_buy_item_id: str = Field(default="", alias="bestBuyItemId")
    low_price_guarantee: bool = Field(alias="lowPriceGuarantee")
    outlet_center: Optional[str] = Field(default=None, alias="outletCenter")
    secondary_market: Optional[str] = Field(default=None, alias="secondaryMarket")
    marketplace: Optional[str] = None
    listing_id: Optional[str] = Field(default=None, alias="listingId")
    seller_id: Optional[str] = Field(default=None, alias="sellerId")
    lists: List[ProductList] = []
    trade_in_value: str = Field(default="", alias="tradeInValue")
    commerce_sku: int = Field(alias="commerceSku")
    proposition65_warning_message: Optional[str] = Field(
        default=None, alias="proposition65WarningMessage"
    )
    proposition65_warning_type: str = Field(
        default="", alias="proposition65WarningType"
    )

    # Appliance-specific
    capacity_cu_ft: Optional[Union[float, int]] = Field(
        default=None, alias="capacityCuFt"
    )
    capacity_freezer_cu_ft: Optional[Union[float, int]] = Field(
        default=None, alias="capacityFreezerCuFt"
    )
    capacity_refrigerator_cu_ft: Optional[Union[float, int]] = Field(
        default=None, alias="capacityRefrigeratorCuFt"
    )
    counter_depth: Optional[bool] = Field(default=None, alias="counterDepth")
    display_type: Optional[str] = Field(default=None, alias="displayType")
    door_open_alarm: Optional[bool] = Field(default=None, alias="doorOpenAlarm")
    energy_consumption_kwh_per_year: Optional[int] = Field(
        default=None, alias="energyConsumptionKwhPerYear"
    )
    energy_star_qualified: Optional[bool] = Field(
        default=None, alias="energyStarQualified"
    )
    estimated_yearly_operating_costs_usd: Optional[int] = Field(
        default=None, alias="estimatedYearlyOperatingCostsUsd"
    )
    factory_installed_ice_maker: Optional[bool] = Field(
        default=None, alias="factoryInstalledIceMaker"
    )
    gallon_door_storage: Optional[bool] = Field(default=None, alias="gallonDoorStorage")
    humidity_controlled_crisper: Optional[bool] = Field(
        default=None, alias="humidityControlledCrisper"
    )
    reversible_door_hinge: Optional[bool] = Field(
        default=None, alias="reversibleDoorHinge"
    )
    sabbath_mode: Optional[bool] = Field(default=None, alias="sabbathMode")
    shelf_construction: Optional[str] = Field(default=None, alias="shelfConstruction")
    temperature_control_type: Optional[str] = Field(
        default=None, alias="temperatureControlType"
    )
    water_filtration: Optional[bool] = Field(default=None, alias="waterFiltration")
    water_filter_model_number: Optional[str] = Field(
        default=None, alias="waterFilterModelNumber"
    )

    # Washer/Dryer specific
    agitator_type: Optional[str] = Field(default=None, alias="agitatorType")
    automatic_temperature_control: Optional[bool] = Field(
        default=None, alias="automaticTemperatureControl"
    )
    bleach_dispenser: Optional[bool] = Field(default=None, alias="bleachDispenser")
    child_lock: Optional[bool] = Field(default=None, alias="childLock")
    control_location: Optional[str] = Field(default=None, alias="controlLocation")
    control_type: Optional[str] = Field(default=None, alias="controlType")
    delayed_start: Optional[bool] = Field(default=None, alias="delayedStart")
    drum_and_interior_finish: Optional[str] = Field(
        default=None, alias="drumAndInteriorFinish"
    )
    drying_rack: Optional[bool] = Field(default=None, alias="dryingRack")
    end_of_cycle_signal: Optional[bool] = Field(default=None, alias="endOfCycleSignal")
    fabric_dispenser: Optional[bool] = Field(default=None, alias="fabricDispenser")
    interior_light: Optional[bool] = Field(default=None, alias="interiorLight")
    load_access: Optional[str] = Field(default=None, alias="loadAccess")
    moisture_sensor: Optional[bool] = Field(default=None, alias="moistureSensor")
    pre_wash_dispenser: Optional[bool] = Field(default=None, alias="preWashDispenser")
    second_rinse: Optional[bool] = Field(default=None, alias="secondRinse")
    smart_capable: Optional[bool] = Field(default=None, alias="smartCapable")
    stackable: Optional[bool] = None
    steam: Optional[bool] = None
    vibration_reduction: Optional[bool] = Field(
        default=None, alias="vibrationReduction"
    )

    # TV/Display specific
    brightness_cd_per_sq_m: Optional[str] = Field(
        default=None, alias="brightnessCdPerSqM"
    )
    contrast_ratio: Optional[str] = Field(default=None, alias="contrastRatio")
    product_aspect_ratio: Optional[str] = Field(
        default=None, alias="productAspectRatio"
    )
    screen_refresh_rate_hz: Optional[int] = Field(
        default=None, alias="screenRefreshRateHz"
    )
    screen_size_class_in: Optional[int] = Field(default=None, alias="screenSizeClassIn")
    screen_size_in: Optional[Union[float, int]] = Field(
        default=None, alias="screenSizeIn"
    )
    three_d_ready: Optional[bool] = Field(default=None, alias="threeDReady")
    tv_type: Optional[str] = Field(default=None, alias="tvType")
    v_chip: Optional[bool] = Field(default=None, alias="vChip")

    # Dimensions with stand
    depth_with_stand_in: Optional[Union[float, int]] = Field(
        default=None, alias="depthWithStandIn"
    )
    depth_without_stand_in: Optional[Union[float, int]] = Field(
        default=None, alias="depthWithoutStandIn"
    )
    height_with_stand_in: Optional[Union[float, int]] = Field(
        default=None, alias="heightWithStandIn"
    )
    height_without_stand_in: Optional[Union[float, int]] = Field(
        default=None, alias="heightWithoutStandIn"
    )

    # Dimensions with handles/doors
    depth_including_handles_in: Optional[Union[float, int]] = Field(
        default=None, alias="depthIncludingHandlesIn"
    )
    depth_less_door_in: Optional[Union[float, int]] = Field(
        default=None, alias="depthLessDoorIn"
    )
    depth_with_door_open_in: Optional[Union[float, int]] = Field(
        default=None, alias="depthWithDoorOpenIn"
    )
    depth_without_handles_in: Optional[Union[float, int]] = Field(
        default=None, alias="depthWithoutHandlesIn"
    )
    height_to_top_of_door_hinge_in: Optional[Union[float, int]] = Field(
        default=None, alias="heightToTopOfDoorHingeIn"
    )
    product_height_in: Optional[Union[float, int]] = Field(
        default=None, alias="productHeightIn"
    )

    # Audio/Video connections
    component_video_inputs: Optional[int] = Field(
        default=None, alias="componentVideoInputs"
    )
    component_video_outputs: Optional[int] = Field(
        default=None, alias="componentVideoOutputs"
    )
    composite_video_inputs: Optional[int] = Field(
        default=None, alias="compositeVideoInputs"
    )
    composite_video_outputs: Optional[int] = Field(
        default=None, alias="compositeVideoOutputs"
    )
    dvi_inputs: Optional[int] = Field(default=None, alias="dviInputs")
    dvi_outputs: Optional[int] = Field(default=None, alias="dviOutputs")
    hdmi_inputs: Optional[int] = Field(default=None, alias="hdmiInputs")
    hdmi_outputs: Optional[int] = Field(default=None, alias="hdmiOutputs")
    coaxial_digital_audio_outputs: Optional[bool] = Field(
        default=None, alias="coaxialDigitalAudioOutputs"
    )
    number_of_coaxial_digital_audio_outputs: Optional[int] = Field(
        default=None, alias="numberOfCoaxialDigitalAudioOutputs"
    )
    number_of_optical_digital_audio_outputs: Optional[int] = Field(
        default=None, alias="numberOfOpticalDigitalAudioOutputs"
    )
    optical_digital_audio_outputs: Optional[bool] = Field(
        default=None, alias="opticalDigitalAudioOutputs"
    )

    # Audio system specific
    number_of_channels: Optional[Union[float, int]] = Field(
        default=None, alias="numberOfChannels"
    )
    number_of_speakers: Optional[int] = Field(default=None, alias="numberOfSpeakers")
    peak_power_handling: Optional[int] = Field(default=None, alias="peakPowerHandling")
    total_harmonic_distortion: Optional[str] = Field(
        default=None, alias="totalHarmonicDistortion"
    )
    total_system_power_watts: Optional[int] = Field(
        default=None, alias="totalSystemPowerWatts"
    )
    watts_per_channel: Optional[int] = Field(default=None, alias="wattsPerChannel")
    watts_per_channel_rms: Optional[int] = Field(
        default=None, alias="wattsPerChannelRms"
    )
    wireless_subwoofer: Optional[bool] = Field(default=None, alias="wirelessSubwoofer")

    # Radio specific
    station_presets: Optional[int] = Field(default=None, alias="stationPresets")
    station_presets_am: Optional[int] = Field(default=None, alias="stationPresetsAm")
    station_presets_fm: Optional[int] = Field(default=None, alias="stationPresetsFm")

    # Player specific
    cd_r_rw_compatible: Optional[bool] = Field(default=None, alias="cdRRwCompatible")
    disc_capacity: Optional[int] = Field(default=None, alias="discCapacity")
    dvd_player: Optional[bool] = Field(default=None, alias="dvdPlayer")
    playback_formats: List[PlaybackFormat] = Field(default=[], alias="playbackFormats")
    player_type: Optional[str] = Field(default=None, alias="playerType")

    # Other connectivity
    built_in_digital_camera: Optional[bool] = Field(
        default=None, alias="builtInDigitalCamera"
    )
    ethernet_port: Optional[bool] = Field(default=None, alias="ethernetPort")
    headphone_jacks: Optional[bool] = Field(default=None, alias="headphoneJacks")
    internet_connectable: Optional[bool] = Field(
        default=None, alias="internetConnectable"
    )
    media_card_slot: Optional[bool] = Field(default=None, alias="mediaCardSlot")
    multiroom_capability: Optional[bool] = Field(
        default=None, alias="multiroomCapability"
    )
    rf_antenna_input: Optional[bool] = Field(default=None, alias="rfAntennaInput")
    usb_port: Optional[bool] = Field(default=None, alias="usbPort")
    wifi_built_in: Optional[bool] = Field(default=None, alias="wifiBuiltIn")

    # Other features
    collection: Optional[str] = None
    compact_design: Optional[bool] = Field(default=None, alias="compactDesign")
    door_handle_color: Optional[str] = Field(default=None, alias="doorHandleColor")
    drive_capacity_gb: Optional[int] = Field(default=None, alias="driveCapacityGb")
    drive_connectivity: Optional[str] = Field(default=None, alias="driveConnectivity")
    front_facing_camera: Optional[bool] = Field(default=None, alias="frontFacingCamera")
    language_options: List[LanguageOption] = Field(default=[], alias="languageOptions")
    maximum_output_resolution: Optional[str] = Field(
        default=None, alias="maximumOutputResolution"
    )
    mobile_operating_system: Optional[str] = Field(
        default=None, alias="mobileOperatingSystem"
    )
    mount_bracket_vesa_pattern: Optional[str] = Field(
        default=None, alias="mountBracketVesaPattern"
    )
    noise_reduction: Optional[bool] = Field(default=None, alias="noiseReduction")
    on_screen_display: Optional[bool] = Field(default=None, alias="onScreenDisplay")
    power_source: Optional[str] = Field(default=None, alias="powerSource")
    rear_facing_camera: Optional[bool] = Field(default=None, alias="rearFacingCamera")
    remote_control_type: Optional[str] = Field(default=None, alias="remoteControlType")
    scanner_type: Optional[str] = Field(default=None, alias="scannerType")
    service_provider: Optional[str] = Field(default=None, alias="serviceProvider")
    sleep_timer: Optional[bool] = Field(default=None, alias="sleepTimer")
    surface_finish: Optional[str] = Field(default=None, alias="surfaceFinish")
    device_manufacturer: Optional[str] = Field(default=None, alias="deviceManufacturer")


class ProductsResponse(BaseModel):
    """Response containing a list of products with pagination metadata."""

    model_config = ConfigDict(populate_by_name=True)

    # Pagination metadata
    from_: int = Field(alias="from")
    to: int
    current_page: int = Field(alias="currentPage")
    total: int
    total_pages: int = Field(alias="totalPages")
    query_time: str = Field(alias="queryTime")
    total_time: str = Field(alias="totalTime")
    canonical_url: str = Field(alias="canonicalUrl")
    partial: bool = False

    # Products
    products: List[Product]


# Recommendations API Models


class RecommendationCustomerReviews(BaseModel):
    """Customer review information for a recommended product."""

    model_config = ConfigDict(populate_by_name=True)

    average_score: Optional[float] = Field(default=None, alias="averageScore")
    count: Optional[int] = None


class RecommendationDescriptions(BaseModel):
    """Description information for a recommended product."""

    short: Optional[str] = None


class RecommendationImages(BaseModel):
    """Image URLs for a recommended product."""

    standard: Optional[str] = None


class RecommendationNames(BaseModel):
    """Name information for a recommended product."""

    title: str


class RecommendationPrices(BaseModel):
    """Price information for a recommended product."""

    regular: float
    current: float


class RecommendationLinks(BaseModel):
    """Links for a recommended product."""

    model_config = ConfigDict(populate_by_name=True)

    product: str
    web: str
    add_to_cart: str = Field(alias="addToCart")


class RecommendedProduct(BaseModel):
    """A recommended product from the Recommendations API."""

    model_config = ConfigDict(populate_by_name=True)

    sku: str
    customer_reviews: RecommendationCustomerReviews = Field(alias="customerReviews")
    descriptions: RecommendationDescriptions
    images: RecommendationImages
    names: RecommendationNames
    prices: RecommendationPrices
    links: RecommendationLinks
    rank: int


class RecommendationsContext(BaseModel):
    """Context metadata for recommendations response."""

    model_config = ConfigDict(populate_by_name=True)

    canonical_url: str = Field(alias="canonicalUrl")


class RecommendationsResultSet(BaseModel):
    """Result set metadata for recommendations response."""

    count: int


class RecommendationsMetadata(BaseModel):
    """Metadata for recommendations response."""

    model_config = ConfigDict(populate_by_name=True)

    context: RecommendationsContext
    result_set: RecommendationsResultSet = Field(alias="resultSet")


class RecommendationsResponse(BaseModel):
    """Response from Recommendations API endpoints."""

    metadata: RecommendationsMetadata
    results: List[RecommendedProduct]


# Stores API Models


class StoreDetailedHours(BaseModel):
    """Detailed hours for a specific day."""

    day: str
    date: date
    open: str
    close: str


class StoreService(BaseModel):
    """A service offered at a store."""

    service: str


class CatalogStore(BaseModel):
    """A Best Buy store from the Catalog API."""

    model_config = ConfigDict(populate_by_name=True)

    # Identification
    store_id: int = Field(alias="storeId")
    store_type: Optional[str] = Field(default=None, alias="storeType")
    location_type: Optional[str] = Field(default=None, alias="locationType")

    # Names
    name: str
    long_name: Optional[str] = Field(default=None, alias="longName")

    # Address
    address: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = Field(default=None, alias="postalCode")
    full_postal_code: Optional[str] = Field(default=None, alias="fullPostalCode")
    country: Optional[str] = None

    # Location
    lat: Optional[float] = None
    lng: Optional[float] = None
    location: Optional[str] = None
    distance: Optional[float] = None

    # Contact
    phone: Optional[str] = None

    # Hours
    hours: Optional[str] = None
    hours_am_pm: Optional[str] = Field(default=None, alias="hoursAmPm")
    gmt_offset: Optional[int] = Field(default=None, alias="gmtOffset")
    detailed_hours: List[StoreDetailedHours] = Field(default=[], alias="detailedHours")

    # Services
    services: List[StoreService] = []


class CatalogStoresResponse(BaseModel):
    """Response containing a list of stores with pagination metadata."""

    model_config = ConfigDict(populate_by_name=True)

    # Pagination metadata
    from_: int = Field(alias="from")
    to: int
    current_page: int = Field(alias="currentPage")
    total: int
    total_pages: int = Field(alias="totalPages")
    query_time: str = Field(alias="queryTime")
    total_time: str = Field(alias="totalTime")
    canonical_url: str = Field(alias="canonicalUrl")
    partial: bool = False

    # Stores
    stores: List[CatalogStore]
