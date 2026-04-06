"""Data models for Shopee cross-market listing transfer."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Variation(BaseModel):
    """A product variation (e.g., color/size option)."""

    variation_id: float | None = None
    name: str | None = None
    sku: str | None = None
    price: str | None = None
    stock: str | None = None
    # Per-variation weight/dimensions (shipping_info supports this)
    weight_kg: str | None = None
    length: str | None = None
    width: str | None = None
    height: str | None = None
    # DTS
    days_to_ship: str | None = None


class Product(BaseModel):
    """A unified product assembled from all 5 export files."""

    # Identifiers (from basic_info)
    product_id: float
    parent_sku: str | None = None
    name: str | None = None
    description: str | None = None

    # Category (from media_info / dts_info)
    category_raw: str | None = None  # e.g. "101379 - Stationery/Notebooks..."
    category_id: str | None = None  # extracted numeric ID

    # Media (from media_info)
    cover_image: str | None = None
    images: list[str | None] = Field(default_factory=lambda: [None] * 8)
    size_chart_template: str | None = None
    size_chart_image: str | None = None
    variation_name1: str | None = None
    variation_options_images: list[tuple[str | None, str | None]] = Field(
        default_factory=list
    )  # [(option_name, option_image), ...]

    # Sales (from sales_info) — product-level fields
    min_purchase_qty: str | None = None
    max_purchase_qty: str | None = None
    max_purchase_qty_start_date: str | None = None
    max_purchase_qty_time_period: str | None = None
    max_purchase_qty_end_date: str | None = None

    # Shipping (from shipping_info) — product-level weight/dimensions
    weight_kg: str | None = None
    length: str | None = None
    width: str | None = None
    height: str | None = None

    # DTS (from dts_info)
    non_preorder_dts: float | None = None
    preorder_dts_range: str | None = None
    days_to_ship: str | None = None

    # Variations (from sales_info + shipping_info + dts_info)
    variations: list[Variation] = Field(default_factory=list)

    @property
    def has_variations(self) -> bool:
        return len(self.variations) > 1


class MarketConfig(BaseModel):
    """Configuration for a specific Shopee market."""

    code: str  # e.g. "my", "sg"
    currency: str  # e.g. "MYR", "SGD"
    tld: str  # e.g. "com.my", "sg"
    shipping_channels: list[str] = Field(default_factory=list)
    direct_listing_price_column: str | None = None  # e.g. "Direct Listing Price:SG"


class TransformConfig(BaseModel):
    """Configuration for a specific transformation run."""

    source_market: str  # market code, e.g. "my"
    target_market: str  # market code, e.g. "sg"
    exchange_rate: float | None = None  # source -> target currency rate
    default_shipping: str = "On"  # default shipping toggle for target channels
