"""Outdoor gear e-commerce customer service agent with complex tool responses."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent as PydanticAgent
from pydantic_ai import RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.openai import OpenAIChatModelSettings
from textprompts import load_prompt

from ..sdk.events import MessagePayload, SessionEndPayload, SessionStartPayload
from ..sdk.stream import StreamHelper
from .base import BaseLayercodeAgent, agent

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


# =============================================================================
# Pydantic Models for Strong Typing
# =============================================================================


class ProductWeight(BaseModel):
    """Weight specifications for a product."""

    packed: str = Field(description="Total packed weight")
    minimum: str | None = Field(default=None, description="Minimum trail weight")
    unit: Literal["imperial", "metric"] = "imperial"


class ProductDimensions(BaseModel):
    """Dimension specifications - varies by product type."""

    floor_area_sqft: int | None = Field(default=None, description="Floor area in sq ft")
    peak_height_inches: int | None = Field(default=None, description="Peak height")
    packed_size: str | None = Field(default=None, description="Packed dimensions")
    volume_liters: int | None = Field(default=None, description="Volume for packs")
    torso_fit_range: str | None = Field(default=None, description="Torso fit range")
    hip_belt_range: str | None = Field(default=None, description="Hip belt size range")
    fits_to_height: str | None = Field(default=None, description="Fits person up to height")
    shoulder_girth_inches: int | None = Field(default=None, description="Shoulder girth")
    sizes_available: list[str] | None = Field(default=None, description="Available sizes")
    fit: str | None = Field(default=None, description="Fit type")


class ProductMaterials(BaseModel):
    """Material specifications."""

    fly: str | None = Field(default=None, description="Tent fly material")
    floor: str | None = Field(default=None, description="Tent floor material")
    poles: str | None = Field(default=None, description="Pole material")
    body: str | None = Field(default=None, description="Pack body material")
    frame: str | None = Field(default=None, description="Pack frame material")
    suspension: str | None = Field(default=None, description="Pack suspension")
    shell: str | None = Field(default=None, description="Shell material")
    lining: str | None = Field(default=None, description="Lining material")
    insulation: str | None = Field(default=None, description="Insulation type")
    membrane: str | None = Field(default=None, description="Waterproof membrane")


class TemperatureRating(BaseModel):
    """Temperature rating for sleeping bags."""

    comfort: int = Field(description="Comfort rating")
    lower_limit: int = Field(description="Lower limit rating")
    extreme: int = Field(description="Extreme/survival rating")
    unit: Literal["fahrenheit", "celsius"] = "fahrenheit"


class ProductSpecifications(BaseModel):
    """Product specifications container."""

    weight: ProductWeight
    dimensions: ProductDimensions
    materials: ProductMaterials
    capacity: int | None = Field(default=None, description="Person capacity")
    season_rating: str | None = Field(default=None, description="Season rating")
    waterproof_rating_mm: int | None = Field(default=None, description="Waterproof rating in mm")
    breathability_gm2: int | None = Field(default=None, description="Breathability g/m²/24h")
    max_load_lbs: int | None = Field(default=None, description="Maximum load capacity")
    temperature_rating: TemperatureRating | None = Field(default=None)
    features: list[str] = Field(default_factory=list, description="Product features")


class RatingBreakdown(BaseModel):
    """Detailed rating breakdown."""

    durability: float | None = None
    weight_value: float | None = None
    weather_protection: float | None = None
    ease_of_setup: float | None = None
    livability: float | None = None
    comfort: float | None = None
    organization: float | None = None
    load_carry: float | None = None
    warmth: float | None = None
    packability: float | None = None
    waterproofing: float | None = None
    breathability: float | None = None
    fit: float | None = None
    value: float | None = None


class ProductRatings(BaseModel):
    """Product ratings and reviews."""

    overall: float = Field(ge=0, le=5, description="Overall rating 0-5")
    review_count: int = Field(ge=0, description="Number of reviews")
    breakdown: RatingBreakdown


class WarehouseStock(BaseModel):
    """Stock information per warehouse."""

    location: str
    stock: int = Field(ge=0)
    ships_in_days: int = Field(ge=1)


class ProductAvailability(BaseModel):
    """Product availability information."""

    in_stock: bool
    quantity: int = Field(ge=0)
    warehouses: list[WarehouseStock] = Field(default_factory=list)
    backorder_date: str | None = Field(default=None, description="ISO date if backordered")


class ProductPricing(BaseModel):
    """Product pricing information."""

    regular_price: float = Field(gt=0)
    sale_price: float | None = Field(default=None, gt=0)
    currency: Literal["USD"] = "USD"
    discount_percentage: int = Field(default=0, ge=0, le=100)
    sale_ends: str | None = Field(default=None, description="ISO datetime")


class Product(BaseModel):
    """Complete product model."""

    id: str
    name: str
    brand: str
    category: Literal["tents", "backpacks", "sleeping_bags", "apparel"]
    description: str
    pricing: ProductPricing
    specifications: ProductSpecifications
    ratings: ProductRatings
    availability: ProductAvailability
    certifications: list[str] = Field(default_factory=list)
    related_products: list[str] = Field(default_factory=list)


class ProductSearchResults(BaseModel):
    """Response from product search."""

    type: Literal["product_search_results"] = "product_search_results"
    query: str
    category_filter: str | None
    results_count: int = Field(ge=0)
    products: list[Product]
    suggested_filters: list[str] = Field(default_factory=list)


# --- Order Models ---


class OrderCustomer(BaseModel):
    """Masked customer information."""

    first_name: str
    email_masked: str


class OrderTotals(BaseModel):
    """Order financial totals."""

    subtotal: float = Field(ge=0)
    shipping: float = Field(ge=0)
    tax: float = Field(ge=0)
    discount: float = Field(default=0)
    total: float = Field(ge=0)
    currency: Literal["USD"] = "USD"


class OrderItemOptions(BaseModel):
    """Product options selected for order item."""

    color: str | None = None
    size: str | None = None


class OrderItem(BaseModel):
    """Individual item in an order."""

    product_id: str
    name: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    options: OrderItemOptions = Field(default_factory=OrderItemOptions)
    fulfillment_status: Literal["pending", "processing", "shipped", "delivered"]


class ShippingAddress(BaseModel):
    """Shipping address (partial for privacy)."""

    city: str
    state: str
    zip: str
    country: str = "US"


class DeliveryEstimate(BaseModel):
    """Delivery date range estimate."""

    earliest: str = Field(description="ISO date")
    latest: str = Field(description="ISO date")


class ShippingInfo(BaseModel):
    """Shipping details for an order."""

    method: str
    carrier: str
    tracking_number: str | None = None
    tracking_url: str | None = None
    address: ShippingAddress
    estimated_delivery: DeliveryEstimate


class OrderStatusEntry(BaseModel):
    """Single entry in order status history."""

    status: Literal["placed", "processing", "packed", "shipped", "in_transit", "delivered"]
    timestamp: str = Field(description="ISO datetime")
    note: str


class Order(BaseModel):
    """Complete order model."""

    id: str
    placed_at: str = Field(description="ISO datetime")
    status: Literal["placed", "processing", "packed", "shipped", "in_transit", "delivered"]
    customer: OrderCustomer
    totals: OrderTotals
    items: list[OrderItem]
    shipping: ShippingInfo
    status_history: list[OrderStatusEntry]


class OrderFoundResponse(BaseModel):
    """Response when order is found."""

    type: Literal["order_details"] = "order_details"
    found: Literal[True] = True
    order: Order
    actions_available: list[str]
    support_note: str


class OrderNotFoundHelp(BaseModel):
    """Help info when order not found."""

    format_hint: str
    example: str
    contact: str


class OrderNotFoundResponse(BaseModel):
    """Response when order is not found."""

    type: Literal["order_details"] = "order_details"
    found: Literal[False] = False
    order_number_searched: str
    message: str
    help: OrderNotFoundHelp


# --- Policy Models ---


class StandardReturnRules(BaseModel):
    """Standard return policy rules."""

    window_days: int = Field(gt=0)
    condition_required: str
    refund_method: str
    processing_time: str
    return_shipping_cost: str


class DefectWarrantyRules(BaseModel):
    """Defect warranty rules."""

    window_days: int = Field(gt=0)
    condition_required: str
    refund_method: str
    processing_time: str
    return_shipping_cost: str


class LifetimeRepairRules(BaseModel):
    """Lifetime repair service rules."""

    eligible_brands: list[str]
    service_type: str
    details: str


class ReturnRules(BaseModel):
    """All return policy rules."""

    standard_returns: StandardReturnRules
    defect_warranty: DefectWarrantyRules
    lifetime_repair: LifetimeRepairRules


class PolicyException(BaseModel):
    """Exception to standard policy."""

    category: str
    rule: str
    reason: str


class ReturnRequirement(BaseModel):
    """Item required for return."""

    item: str
    required: bool
    note: str | None = None


class ProcessStep(BaseModel):
    """Step in a process."""

    step: int = Field(gt=0)
    action: str
    details: str | None = None


class ReturnPolicy(BaseModel):
    """Complete return policy."""

    name: str
    policy_type: Literal["returns"] = "returns"
    last_updated: str
    summary: str
    rules: ReturnRules
    exceptions: list[PolicyException]
    required_for_return: list[ReturnRequirement]
    process_steps: list[ProcessStep]
    contact_for_exceptions: str


class ShippingOption(BaseModel):
    """Available shipping option."""

    method: str
    price: float = Field(ge=0)
    free_threshold: float | None = None
    delivery_estimate: str
    carrier: str


class POBoxRestriction(BaseModel):
    """PO Box shipping restriction."""

    allowed: bool
    methods: list[str]
    note: str


class RegionalRestriction(BaseModel):
    """Regional shipping restriction."""

    allowed: bool
    surcharge: float | None = None
    additional_days: int | None = None
    note: str | None = None


class ShippingRestrictions(BaseModel):
    """All shipping restrictions."""

    po_boxes: POBoxRestriction
    alaska_hawaii: RegionalRestriction
    international: RegionalRestriction


class PeakSeasonDates(BaseModel):
    """Peak season date range."""

    start: str
    end: str


class ProcessingTime(BaseModel):
    """Order processing time info."""

    standard: str
    peak_season: str
    peak_season_dates: PeakSeasonDates


class TrackingInfo(BaseModel):
    """Tracking notification info."""

    provided: bool
    notification_methods: list[str]
    updates_frequency: str


class ShippingPolicy(BaseModel):
    """Complete shipping policy."""

    name: str
    policy_type: Literal["shipping"] = "shipping"
    last_updated: str
    summary: str
    shipping_options: list[ShippingOption]
    restrictions: ShippingRestrictions
    processing_time: ProcessingTime
    tracking: TrackingInfo


class WarrantyTier(BaseModel):
    """Warranty tier definition."""

    tier: str
    duration: str
    coverage: str
    exclusions: list[str]


class WarrantyClaimStep(BaseModel):
    """Step in warranty claim process."""

    step: int = Field(gt=0)
    action: str


class WarrantyClaimProcess(BaseModel):
    """Warranty claim process details."""

    steps: list[WarrantyClaimStep]
    response_time: str
    resolution_time: str


class WarrantyPolicy(BaseModel):
    """Complete warranty policy."""

    name: str
    policy_type: Literal["warranty"] = "warranty"
    last_updated: str
    summary: str
    warranty_tiers: list[WarrantyTier]
    claim_process: WarrantyClaimProcess
    important_notes: list[str]


class PolicyFoundResponse(BaseModel):
    """Response when policy is found."""

    type: Literal["policy_details"] = "policy_details"
    found: Literal[True] = True
    policy: ReturnPolicy | ShippingPolicy | WarrantyPolicy
    related_policies: list[str]


class PolicyNotFoundResponse(BaseModel):
    """Response when policy is not found."""

    type: Literal["policy_details"] = "policy_details"
    found: Literal[False] = False
    policy_type_searched: str
    available_policies: list[str]
    message: str


# =============================================================================
# Mock Data (typed with models)
# =============================================================================

PRODUCT_CATALOG: dict[str, Product] = {
    "TENT-UL-2P": Product(
        id="TENT-UL-2P",
        name="Nimbus CloudLite 2P",
        brand="Nimbus Gear",
        category="tents",
        description="Ultralight 2-person backpacking tent with weather protection.",
        pricing=ProductPricing(
            regular_price=449.99,
            sale_price=379.99,
            discount_percentage=16,
            sale_ends="2025-12-15T00:00:00Z",
        ),
        specifications=ProductSpecifications(
            weight=ProductWeight(packed="2 lbs 4 oz", minimum="1 lb 14 oz"),
            dimensions=ProductDimensions(
                floor_area_sqft=28, peak_height_inches=42, packed_size="5x18 inches"
            ),
            materials=ProductMaterials(fly="15D Silnylon", floor="20D Nylon", poles="DAC NSL"),
            capacity=2,
            season_rating="3-season",
            waterproof_rating_mm=3000,
        ),
        ratings=ProductRatings(
            overall=4.7,
            review_count=234,
            breakdown=RatingBreakdown(
                durability=4.5,
                weight_value=4.9,
                weather_protection=4.6,
                ease_of_setup=4.8,
                livability=4.3,
            ),
        ),
        availability=ProductAvailability(
            in_stock=True,
            quantity=23,
            warehouses=[
                WarehouseStock(location="Denver, CO", stock=15, ships_in_days=1),
                WarehouseStock(location="Seattle, WA", stock=8, ships_in_days=2),
            ],
        ),
        certifications=["bluesign approved", "Climate Neutral Certified"],
        related_products=["FOOTPRINT-CL2P", "GUYLINE-REFL-4PK", "STAKES-UL-6PK"],
    ),
    "TENT-4S-2P": Product(
        id="TENT-4S-2P",
        name="Nimbus StormShield 2P",
        brand="Nimbus Gear",
        category="tents",
        description="4-season tent for alpine conditions and winter camping.",
        pricing=ProductPricing(regular_price=699.99),
        specifications=ProductSpecifications(
            weight=ProductWeight(packed="5 lbs 8 oz", minimum="4 lbs 12 oz"),
            dimensions=ProductDimensions(
                floor_area_sqft=32, peak_height_inches=44, packed_size="7x22 inches"
            ),
            materials=ProductMaterials(
                fly="40D Ripstop Nylon", floor="70D Nylon", poles="Easton Syclone"
            ),
            capacity=2,
            season_rating="4-season",
            waterproof_rating_mm=5000,
        ),
        ratings=ProductRatings(
            overall=4.9,
            review_count=87,
            breakdown=RatingBreakdown(
                durability=5.0,
                weight_value=4.2,
                weather_protection=5.0,
                ease_of_setup=4.5,
                livability=4.6,
            ),
        ),
        availability=ProductAvailability(
            in_stock=True,
            quantity=12,
            warehouses=[
                WarehouseStock(location="Denver, CO", stock=8, ships_in_days=1),
                WarehouseStock(location="Seattle, WA", stock=4, ships_in_days=2),
            ],
        ),
        certifications=["bluesign approved"],
        related_products=["FOOTPRINT-SS2P", "SNOW-STAKES-4PK"],
    ),
    "PACK-UL-45": Product(
        id="PACK-UL-45",
        name="Nimbus TrailSwift 45L",
        brand="Nimbus Gear",
        category="backpacks",
        description="Ultralight 45L pack for multi-day fastpacking.",
        pricing=ProductPricing(
            regular_price=289.99,
            sale_price=259.99,
            discount_percentage=10,
            sale_ends="2025-12-20T00:00:00Z",
        ),
        specifications=ProductSpecifications(
            weight=ProductWeight(packed="1 lb 12 oz"),
            dimensions=ProductDimensions(
                volume_liters=45, torso_fit_range="15-21 inches", hip_belt_range="28-42 inches"
            ),
            materials=ProductMaterials(
                body="100D Robic Nylon", frame="HDPE framesheet", suspension="Mesh back panel"
            ),
            max_load_lbs=30,
            features=["Roll-top closure", "Side water bottle pockets", "Hip belt pockets"],
        ),
        ratings=ProductRatings(
            overall=4.6,
            review_count=156,
            breakdown=RatingBreakdown(
                comfort=4.5, weight_value=4.9, durability=4.3, organization=4.4, load_carry=4.6
            ),
        ),
        availability=ProductAvailability(
            in_stock=True,
            quantity=45,
            warehouses=[
                WarehouseStock(location="Denver, CO", stock=20, ships_in_days=1),
                WarehouseStock(location="Seattle, WA", stock=15, ships_in_days=2),
                WarehouseStock(location="Portland, ME", stock=10, ships_in_days=3),
            ],
        ),
        certifications=["Climate Neutral Certified"],
        related_products=["RAIN-COVER-45", "PACK-CUBE-SET"],
    ),
    "SLEEP-DOWN-20": Product(
        id="SLEEP-DOWN-20",
        name="Nimbus DreamLoft 20F",
        brand="Nimbus Gear",
        category="sleeping_bags",
        description="800-fill down sleeping bag rated to 20F.",
        pricing=ProductPricing(regular_price=399.99),
        specifications=ProductSpecifications(
            weight=ProductWeight(packed="2 lbs 2 oz"),
            dimensions=ProductDimensions(
                fits_to_height="6 ft 0 in", shoulder_girth_inches=62, packed_size="8x15 inches"
            ),
            materials=ProductMaterials(
                shell="15D Ripstop Nylon", lining="20D Taffeta", insulation="800-fill RDS Down"
            ),
            temperature_rating=TemperatureRating(comfort=28, lower_limit=20, extreme=-2),
            features=["Draft collar", "Zipper draft tube", "Stash pocket"],
        ),
        ratings=ProductRatings(
            overall=4.8,
            review_count=312,
            breakdown=RatingBreakdown(
                warmth=4.9, weight_value=4.7, packability=4.8, comfort=4.6, durability=4.7
            ),
        ),
        availability=ProductAvailability(
            in_stock=False, quantity=0, warehouses=[], backorder_date="2025-12-10"
        ),
        certifications=["RDS Certified", "bluesign approved"],
        related_products=["SLEEP-LINER-SILK", "STUFF-SACK-COMP"],
    ),
    "JACKET-RAIN-M": Product(
        id="JACKET-RAIN-M",
        name="Nimbus StormGuard Jacket",
        brand="Nimbus Gear",
        category="apparel",
        description="Lightweight waterproof-breathable shell.",
        pricing=ProductPricing(
            regular_price=249.99,
            sale_price=199.99,
            discount_percentage=20,
            sale_ends="2025-12-08T00:00:00Z",
        ),
        specifications=ProductSpecifications(
            weight=ProductWeight(packed="10.5 oz"),
            dimensions=ProductDimensions(
                sizes_available=["XS", "S", "M", "L", "XL", "XXL"], fit="Regular"
            ),
            materials=ProductMaterials(
                shell="3L Waterproof-Breathable Nylon",
                membrane="NimbusShield Pro",
                lining="Tricot backer",
            ),
            waterproof_rating_mm=20000,
            breathability_gm2=25000,
            features=["Fully taped seams", "Helmet-compatible hood", "Pit zips", "Napoleon pocket"],
        ),
        ratings=ProductRatings(
            overall=4.5,
            review_count=423,
            breakdown=RatingBreakdown(
                waterproofing=4.8, breathability=4.4, fit=4.5, durability=4.3, value=4.6
            ),
        ),
        availability=ProductAvailability(
            in_stock=True,
            quantity=89,
            warehouses=[
                WarehouseStock(location="Denver, CO", stock=35, ships_in_days=1),
                WarehouseStock(location="Seattle, WA", stock=30, ships_in_days=2),
                WarehouseStock(location="Portland, ME", stock=24, ships_in_days=3),
            ],
        ),
        certifications=["bluesign approved", "Fair Trade Certified"],
        related_products=["PANTS-RAIN-M", "HAT-WATERPROOF"],
    ),
}

ORDERS_DB: dict[str, Order] = {
    "NG-2025-78234": Order(
        id="NG-2025-78234",
        placed_at="2025-11-28T14:32:00Z",
        status="in_transit",
        customer=OrderCustomer(first_name="Alex", email_masked="a***n@email.com"),
        totals=OrderTotals(subtotal=459.98, shipping=0.00, tax=36.80, discount=0.00, total=496.78),
        items=[
            OrderItem(
                product_id="TENT-UL-2P",
                name="Nimbus CloudLite 2P",
                quantity=1,
                unit_price=379.99,
                options=OrderItemOptions(color="Forest Green"),
                fulfillment_status="shipped",
            ),
            OrderItem(
                product_id="FOOTPRINT-CL2P",
                name="CloudLite 2P Footprint",
                quantity=1,
                unit_price=79.99,
                options=OrderItemOptions(),
                fulfillment_status="shipped",
            ),
        ],
        shipping=ShippingInfo(
            method="Ground",
            carrier="UPS",
            tracking_number="1Z999AA10123456784",
            tracking_url="https://ups.com/track?num=1Z999AA10123456784",
            address=ShippingAddress(city="Boulder", state="CO", zip="80301"),
            estimated_delivery=DeliveryEstimate(earliest="2025-12-03", latest="2025-12-05"),
        ),
        status_history=[
            OrderStatusEntry(
                status="placed", timestamp="2025-11-28T14:32:00Z", note="Order confirmed"
            ),
            OrderStatusEntry(
                status="processing", timestamp="2025-11-28T16:45:00Z", note="Payment verified"
            ),
            OrderStatusEntry(
                status="packed", timestamp="2025-11-29T09:12:00Z", note="Packed at Denver"
            ),
            OrderStatusEntry(
                status="shipped", timestamp="2025-11-29T14:30:00Z", note="Handed to UPS"
            ),
            OrderStatusEntry(
                status="in_transit", timestamp="2025-11-30T08:00:00Z", note="In transit - Denver"
            ),
        ],
    ),
    "NG-2025-81456": Order(
        id="NG-2025-81456",
        placed_at="2025-12-01T09:15:00Z",
        status="processing",
        customer=OrderCustomer(first_name="Jordan", email_masked="j***n@email.com"),
        totals=OrderTotals(
            subtotal=259.99, shipping=12.99, tax=21.84, discount=-30.00, total=264.82
        ),
        items=[
            OrderItem(
                product_id="PACK-UL-45",
                name="Nimbus TrailSwift 45L",
                quantity=1,
                unit_price=259.99,
                options=OrderItemOptions(color="Midnight Blue", size="M/L"),
                fulfillment_status="pending",
            ),
        ],
        shipping=ShippingInfo(
            method="Standard",
            carrier="USPS",
            tracking_number=None,
            tracking_url=None,
            address=ShippingAddress(city="Portland", state="OR", zip="97201"),
            estimated_delivery=DeliveryEstimate(earliest="2025-12-06", latest="2025-12-10"),
        ),
        status_history=[
            OrderStatusEntry(
                status="placed", timestamp="2025-12-01T09:15:00Z", note="Order confirmed"
            ),
            OrderStatusEntry(
                status="processing", timestamp="2025-12-01T10:30:00Z", note="Payment verified"
            ),
        ],
    ),
}

POLICIES: dict[str, ReturnPolicy | ShippingPolicy | WarrantyPolicy] = {
    "returns": ReturnPolicy(
        name="Return & Exchange Policy",
        last_updated="2025-09-01",
        summary="60-day guarantee on unused gear; 1-year warranty on defects.",
        rules=ReturnRules(
            standard_returns=StandardReturnRules(
                window_days=60,
                condition_required="unused_with_tags",
                refund_method="original_payment",
                processing_time="5-7 business days",
                return_shipping_cost="customer_responsibility",
            ),
            defect_warranty=DefectWarrantyRules(
                window_days=365,
                condition_required="manufacturing_defect",
                refund_method="replacement_or_refund",
                processing_time="7-10 business days",
                return_shipping_cost="prepaid_label_provided",
            ),
            lifetime_repair=LifetimeRepairRules(
                eligible_brands=["Nimbus Gear"],
                service_type="repair_at_cost",
                details="We repair our own gear for life at material cost only",
            ),
        ),
        exceptions=[
            PolicyException(
                category="Final Sale Items",
                rule="no_returns",
                reason="Clearance items marked 'Final Sale'",
            ),
            PolicyException(
                category="Hygiene Items",
                rule="unopened_only",
                reason="Filters, bladders, base layers must be sealed",
            ),
            PolicyException(
                category="Custom Orders",
                rule="no_returns",
                reason="Personalized items cannot be returned",
            ),
        ],
        required_for_return=[
            ReturnRequirement(item="Order number or receipt", required=True),
            ReturnRequirement(item="Original packaging", required=False, note="Preferred"),
            ReturnRequirement(item="All included accessories", required=True),
            ReturnRequirement(item="Reason for return", required=True),
        ],
        process_steps=[
            ProcessStep(step=1, action="Initiate at nimbusgear.com/returns", details="Log in"),
            ProcessStep(step=2, action="Select items and reason", details="Photos help"),
            ProcessStep(step=3, action="Print shipping label", details="Prepaid for defects"),
            ProcessStep(step=4, action="Ship within 7 days", details="Any UPS location"),
            ProcessStep(step=5, action="Refund on receipt", details="Email confirmation sent"),
        ],
        contact_for_exceptions="returns@nimbusgear.com",
    ),
    "shipping": ShippingPolicy(
        name="Shipping Policy",
        last_updated="2025-10-15",
        summary="Free shipping over $99. Multiple speed options.",
        shipping_options=[
            ShippingOption(
                method="Standard Ground",
                price=7.99,
                free_threshold=99.00,
                delivery_estimate="5-7 business days",
                carrier="USPS/UPS",
            ),
            ShippingOption(
                method="Expedited",
                price=14.99,
                delivery_estimate="3-4 business days",
                carrier="UPS",
            ),
            ShippingOption(
                method="Express",
                price=24.99,
                delivery_estimate="1-2 business days",
                carrier="UPS Next Day Air",
            ),
        ],
        restrictions=ShippingRestrictions(
            po_boxes=POBoxRestriction(
                allowed=True, methods=["Standard Ground"], note="USPS only for PO Boxes"
            ),
            alaska_hawaii=RegionalRestriction(allowed=True, surcharge=15.00, additional_days=3),
            international=RegionalRestriction(allowed=False, note="US addresses only"),
        ),
        processing_time=ProcessingTime(
            standard="1-2 business days",
            peak_season="2-3 business days",
            peak_season_dates=PeakSeasonDates(start="2025-11-15", end="2025-12-31"),
        ),
        tracking=TrackingInfo(
            provided=True,
            notification_methods=["email", "sms_opt_in"],
            updates_frequency="Each scan",
        ),
    ),
    "warranty": WarrantyPolicy(
        name="Product Warranty",
        last_updated="2025-06-01",
        summary="Nimbus Gear products backed by quality promise.",
        warranty_tiers=[
            WarrantyTier(
                tier="Nimbus Gear Products",
                duration="Lifetime limited warranty",
                coverage="Manufacturing defects in materials and workmanship",
                exclusions=[
                    "Normal wear and tear",
                    "Misuse or accidents",
                    "Unauthorized modifications",
                    "Cosmetic damage",
                ],
            ),
            WarrantyTier(
                tier="Partner Brand Products",
                duration="Varies by manufacturer",
                coverage="Per manufacturer terms",
                exclusions=["See product warranty card"],
            ),
        ],
        claim_process=WarrantyClaimProcess(
            steps=[
                WarrantyClaimStep(step=1, action="Document defect with photos"),
                WarrantyClaimStep(step=2, action="Contact warranty@nimbusgear.com"),
                WarrantyClaimStep(step=3, action="Receive RMA and instructions"),
                WarrantyClaimStep(step=4, action="Ship item for inspection"),
                WarrantyClaimStep(step=5, action="Receive repair/replacement/credit"),
            ],
            response_time="24-48 hours",
            resolution_time="7-14 business days",
        ),
        important_notes=[
            "Keep receipt for warranty claims",
            "Register gear at nimbusgear.com/register",
            "Warranty non-transferable",
        ],
    ),
}


# =============================================================================
# Agent Implementation
# =============================================================================


@agent("outdoor_shop")
class OutdoorShopAgent(BaseLayercodeAgent):
    """Customer service agent for Nimbus Gear outdoor equipment store."""

    name = "outdoor_shop"
    description = "Outdoor gear e-commerce customer service with complex data responses"

    def __init__(self, model: str) -> None:
        super().__init__(model)

        prompt = load_prompt(PROMPTS_DIR / "outdoor_shop.txt", meta="strict")
        system_prompt = str(prompt.prompt)

        model_settings = None
        if model == "openai:gpt-5-nano":
            model_settings = OpenAIChatModelSettings(openai_reasoning_effort="minimal")

        self._agent = PydanticAgent(
            model,
            system_prompt=system_prompt,
            deps_type=StreamHelper,
            model_settings=model_settings,
        )

        @self._agent.tool
        async def search_products(
            ctx: RunContext[StreamHelper],
            query: str,
            category: str | None = None,
            max_results: int = 3,
        ) -> ProductSearchResults:
            """Search the product catalog by keyword and optional category.

            Note: This is a simplified demo. If no exact matches are found, returns
            a sample of products from the catalog to ensure non-empty results for
            testing purposes.

            Args:
                query: Search terms (e.g., 'ultralight tent', 'rain jacket')
                category: Optional filter: tents, backpacks, sleeping_bags, apparel
                max_results: Maximum products to return (default 3)
            """
            stream = ctx.deps
            query_lower = query.lower()

            matches: list[Product] = []
            for product in PRODUCT_CATALOG.values():
                if category and product.category != category.lower():
                    continue
                searchable = f"{product.name} {product.description} {product.category}"
                if query_lower in searchable.lower():
                    matches.append(product)
                if len(matches) >= max_results:
                    break

            # Fallback: return sample products when no matches found (demo simplification)
            if not matches:
                for product in PRODUCT_CATALOG.values():
                    if category and product.category != category.lower():
                        continue
                    matches.append(product)
                    if len(matches) >= max_results:
                        break

            result = ProductSearchResults(
                query=query,
                category_filter=category,
                results_count=len(matches),
                products=matches,
                suggested_filters=_get_suggested_filters(matches),
            )

            stream.data(
                {
                    "tool": "search_products",
                    "event_type": "product_catalog",
                    "query": query,
                    "results_count": len(matches),
                    "payload": result.model_dump(),
                }
            )

            return result

        @self._agent.tool
        async def lookup_order(
            ctx: RunContext[StreamHelper],
            order_number: str,
        ) -> OrderFoundResponse | OrderNotFoundResponse:
            """Look up order status and tracking information.

            Args:
                order_number: The order ID (e.g., 'NG-2025-78234')
            """
            stream = ctx.deps
            order_upper = order_number.upper().strip()

            if order_upper in ORDERS_DB:
                order = ORDERS_DB[order_upper]
                result: OrderFoundResponse | OrderNotFoundResponse = OrderFoundResponse(
                    order=order,
                    actions_available=_get_available_actions(order),
                    support_note="For modifications, contact support@nimbusgear.com",
                )
            else:
                result = OrderNotFoundResponse(
                    order_number_searched=order_upper,
                    message="Order not found. Please verify the order number.",
                    help=OrderNotFoundHelp(
                        format_hint="Order numbers start with 'NG-' followed by year and number",
                        example="NG-2024-12345",
                        contact="support@nimbusgear.com",
                    ),
                )

            stream.data(
                {
                    "tool": "lookup_order",
                    "event_type": "order_tracking",
                    "order_number": order_upper,
                    "found": result.found,
                    "payload": result.model_dump(),
                }
            )

            return result

        @self._agent.tool
        async def get_policy(
            ctx: RunContext[StreamHelper],
            policy_type: str,
        ) -> PolicyFoundResponse | PolicyNotFoundResponse:
            """Retrieve store policy information.

            Args:
                policy_type: Type of policy: 'returns', 'shipping', or 'warranty'
            """
            stream = ctx.deps
            policy_key = policy_type.lower().strip()

            if policy_key in POLICIES:
                policy = POLICIES[policy_key]
                result: PolicyFoundResponse | PolicyNotFoundResponse = PolicyFoundResponse(
                    policy=policy,
                    related_policies=[p for p in POLICIES.keys() if p != policy_key],
                )
            else:
                result = PolicyNotFoundResponse(
                    policy_type_searched=policy_type,
                    available_policies=list(POLICIES.keys()),
                    message=f"Policy '{policy_type}' not found.",
                )

            stream.data(
                {
                    "tool": "get_policy",
                    "event_type": "policy_info",
                    "policy_type": policy_key,
                    "found": result.found,
                    "payload": result.model_dump(),
                }
            )

            return result

    def pydantic_agent(self) -> object | None:
        return self._agent

    async def handle_session_start(
        self, payload: SessionStartPayload, stream: StreamHelper
    ) -> None:
        stream.tts("Nimbus Gear support. How can I help?")
        stream.end()

    async def handle_message(
        self,
        payload: MessagePayload,
        stream: StreamHelper,
        history: list[ModelMessage],
    ) -> list[ModelMessage]:
        user_text = payload.text or ""

        async with self._agent.run_stream(user_text, deps=stream, message_history=history) as run:
            streamed = False
            async for chunk in run.stream_text(delta=True):
                if chunk:
                    streamed = True
                    stream.tts(chunk)

            final_text = await run.get_output()
            if final_text and not streamed:
                stream.tts(final_text)

            new_messages = list(run.new_messages())

        stream.end()
        return new_messages

    async def handle_session_end(self, payload: SessionEndPayload) -> None:
        pass


def _get_suggested_filters(products: list[Product]) -> list[str]:
    """Generate suggested filters based on search results."""
    filters: set[str] = set()
    for p in products:
        if p.specifications.season_rating:
            filters.add(p.specifications.season_rating)
        if p.specifications.capacity:
            filters.add(f"{p.specifications.capacity}-person")
        filters.add(p.category)
    return sorted(filters)[:5]


def _get_available_actions(order: Order) -> list[str]:
    """Determine available actions based on order status."""
    actions = ["contact_support"]
    if order.status in ("shipped", "in_transit"):
        actions.insert(0, "track_package")
    if order.status == "processing":
        actions.insert(0, "request_cancellation")
    if order.status == "delivered":
        actions.insert(0, "initiate_return")
    return actions
