"""Core transformation: map exported products to upload template format."""

from __future__ import annotations

from .config import load_category_mapping, load_market_config
from .currency import convert_price
from .models import MarketConfig, Product, TransformConfig, Variation


def _map_category(
    product: Product,
    category_mapping: dict[str, str],
) -> str | None:
    """Map source category ID to target category ID."""
    if not product.category_id:
        return None
    mapped = category_mapping.get(product.category_id)
    if mapped:
        return mapped
    # If no mapping exists, return the source ID as-is (seller can fix in upload)
    return product.category_id


def transform_products(
    products: list[Product],
    config: TransformConfig,
    config_dir=None,
    category_overrides: dict[str, str] | None = None,
) -> list[dict]:
    """Transform a list of Products into rows for the upload template.

    Returns a list of dicts, each representing one row in the upload file.
    Products without variations produce 1 row.
    Products with N variations produce N rows (first has product-level info,
    subsequent rows have only variation-level info).

    Args:
        category_overrides: Optional dict of source category ID -> target category ID
            that takes precedence over the mapping file. Used by the web UI.
    """
    source_config = load_market_config(config.source_market, config_dir)
    target_config = load_market_config(config.target_market, config_dir)
    category_mapping = load_category_mapping(
        config.source_market, config.target_market, config_dir
    )
    if category_overrides:
        category_mapping.update(category_overrides)

    rows: list[dict] = []
    integration_counter = 1

    for product in products:
        mapped_category = _map_category(product, category_mapping)

        if not product.variations or len(product.variations) <= 1:
            # Single product (no variations or exactly 1 variation = no split)
            row = _build_product_row(
                product, product.variations[0] if product.variations else None,
                mapped_category, source_config, target_config, config,
                integration_no=None,
            )
            rows.append(row)
        else:
            # Multi-variation product
            integration_no = str(integration_counter)
            integration_counter += 1

            for i, variation in enumerate(product.variations):
                is_first = i == 0
                row = _build_variation_row(
                    product, variation, mapped_category,
                    source_config, target_config, config,
                    integration_no, is_first,
                )
                rows.append(row)

    return rows


def _convert(
    price_str: str | None,
    source_config: MarketConfig,
    target_config: MarketConfig,
    config: TransformConfig,
) -> str | None:
    """Convert price using config settings."""
    if price_str is None:
        return None
    return convert_price(
        price_str,
        source_config.currency,
        target_config.currency,
        config.exchange_rate,
    )


def _build_product_row(
    product: Product,
    variation: Variation | None,
    mapped_category: str | None,
    source_config: MarketConfig,
    target_config: MarketConfig,
    config: TransformConfig,
    integration_no: str | None,
) -> dict:
    """Build a single upload row for a product without multiple variations."""
    converted_price = _convert(
        variation.price if variation else None,
        source_config, target_config, config,
    )

    row = {
        "Category": mapped_category,
        "Product Name": product.name,
        "Product Description": product.description,
        "Maximum Purchase Quantity": product.max_purchase_qty,
        "Maximum Purchase Quantity - Start Date": product.max_purchase_qty_start_date,
        "Maximum Purchase Quantity - Time Period (in Days)": product.max_purchase_qty_time_period,
        "Maximum Purchase Quantity - End Date": product.max_purchase_qty_end_date,
        "Minimum Purchase Quantity": product.min_purchase_qty,
        "Parent SKU": product.parent_sku,
        "Dangerous Goods": None,
        "Variation Integration No.": integration_no,
        "Variation Name1": product.variation_name1 if product.has_variations else None,
        "Option for Variation 1": variation.name if variation and product.has_variations else None,
        "Image per Variation": None,
        "Variation Name2": None,
        "Option for Variation 2": None,
        "Price": converted_price,
        "Stock": variation.stock if variation else None,
        "SKU": variation.sku if variation else None,
        "Size Chart Template": product.size_chart_template,
        "Size Chart Image": product.size_chart_image,
        "GTIN": None,
        "Cover image": product.cover_image,
        "Weight": product.weight_kg,
        "Length": product.length,
        "Width": product.width,
        "Height": product.height,
        "Pre-order DTS": None,
    }

    # Add images
    for i in range(8):
        row[f"Item Image {i + 1}"] = product.images[i] if i < len(product.images) else None

    # Set shipping channels to default "On" for target market
    for channel in target_config.shipping_channels:
        row[channel] = config.default_shipping

    # Handle Direct Listing Price (market-specific, e.g. SG has "Direct Listing Price:SG")
    if target_config.direct_listing_price_column:
        row[target_config.direct_listing_price_column] = converted_price

    return row


def _build_variation_row(
    product: Product,
    variation: Variation,
    mapped_category: str | None,
    source_config: MarketConfig,
    target_config: MarketConfig,
    config: TransformConfig,
    integration_no: str,
    is_first: bool,
) -> dict:
    """Build an upload row for a product variation.

    First variation row includes all product-level info.
    Subsequent rows only include variation-specific fields.
    """
    converted_price = _convert(variation.price, source_config, target_config, config)

    if is_first:
        # First row: full product + variation info
        row = _build_product_row(
            product, variation, mapped_category,
            source_config, target_config, config,
            integration_no,
        )
        # Map variation image from media_info option images
        row["Image per Variation"] = _find_variation_image(product, variation)

        return row
    else:
        # Subsequent rows: only variation-specific fields
        row = {
            "Category": None,
            "Product Name": None,
            "Product Description": None,
            "Maximum Purchase Quantity": None,
            "Maximum Purchase Quantity - Start Date": None,
            "Maximum Purchase Quantity - Time Period (in Days)": None,
            "Maximum Purchase Quantity - End Date": None,
            "Minimum Purchase Quantity": None,
            "Parent SKU": None,
            "Dangerous Goods": None,
            "Variation Integration No.": integration_no,
            "Variation Name1": None,
            "Option for Variation 1": variation.name,
            "Image per Variation": _find_variation_image(product, variation),
            "Variation Name2": None,
            "Option for Variation 2": None,
            "Price": converted_price,
            "Stock": variation.stock,
            "SKU": variation.sku,
            "Size Chart Template": None,
            "Size Chart Image": None,
            "GTIN": None,
            "Cover image": None,
            "Weight": variation.weight_kg or product.weight_kg,
            "Length": variation.length,
            "Width": variation.width,
            "Height": variation.height,
            "Pre-order DTS": None,
        }

        if target_config.direct_listing_price_column:
            row[target_config.direct_listing_price_column] = converted_price

        for i in range(8):
            row[f"Item Image {i + 1}"] = None

        for channel in target_config.shipping_channels:
            row[channel] = None

        return row


def _find_variation_image(product: Product, variation: Variation) -> str | None:
    """Find the image for a specific variation option from media_info data."""
    if not variation.name or not product.variation_options_images:
        return None
    for opt_name, opt_img in product.variation_options_images:
        if opt_name and opt_name == variation.name:
            return opt_img
    return None
