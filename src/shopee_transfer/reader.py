"""Parse Shopee Mass Update export Excel files and merge into Product objects."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .models import Product, Variation

# Export type detection: row 0, col 0 contains the type identifier
EXPORT_TYPES = {
    "basic_info": {"header_row": 2, "level": "product"},
    "sales_info": {"header_row": 2, "level": "variation"},
    "shipping_info": {"header_row": 3, "level": "variation"},
    "dts_info": {"header_row": 2, "level": "variation"},
    "media_info": {"header_row": 2, "level": "product"},
}


def detect_export_type(path: str | Path) -> str:
    """Detect the export type from the metadata row (row 1, col 0)."""
    # Row 1 col 0 contains the type identifier: "basic_info", "sales_info", etc.
    df_row1 = pd.read_excel(path, engine="calamine", header=None, skiprows=1, nrows=1)
    export_type = str(df_row1.iloc[0, 0])
    if export_type in EXPORT_TYPES:
        return export_type
    raise ValueError(f"Unknown export type: {export_type} (from {path})")


def read_export(path: str | Path) -> tuple[str, pd.DataFrame]:
    """Read an export file and return (export_type, dataframe with data rows only)."""
    export_type = detect_export_type(path)
    config = EXPORT_TYPES[export_type]
    header_row = config["header_row"]

    df = pd.read_excel(path, engine="calamine", header=header_row)

    # Skip instruction/description rows that follow the header.
    # Data rows have a numeric Product ID in the first column.
    pid_col = "Product ID"
    if pid_col not in df.columns:
        raise ValueError(f"'{pid_col}' column not found in {path}. Columns: {list(df.columns)}")

    # Filter to rows where Product ID is a valid number
    df = df[pd.to_numeric(df[pid_col], errors="coerce").notna()].copy()
    df[pid_col] = pd.to_numeric(df[pid_col])

    return export_type, df


def _safe_str(val) -> str | None:
    """Convert a value to string, returning None for NaN/empty."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    return s if s else None


def _parse_basic_info(products: dict[float, Product], df: pd.DataFrame) -> None:
    """Merge basic_info data into products dict."""
    for _, row in df.iterrows():
        pid = float(row["Product ID"])
        if pid not in products:
            products[pid] = Product(product_id=pid)
        p = products[pid]
        p.name = _safe_str(row.get("Product Name"))
        p.description = _safe_str(row.get("Product Description"))
        if p.parent_sku is None:
            p.parent_sku = _safe_str(row.get("Parent SKU"))


def _parse_media_info(products: dict[float, Product], df: pd.DataFrame) -> None:
    """Merge media_info data into products dict."""
    for _, row in df.iterrows():
        pid = float(row["Product ID"])
        if pid not in products:
            products[pid] = Product(product_id=pid)
        p = products[pid]
        p.category_raw = _safe_str(row.get("Category"))
        if p.category_raw:
            # Extract numeric ID from "101379 - Stationery/..."
            parts = p.category_raw.split(" - ", 1)
            p.category_id = parts[0].strip() if parts else None
        p.cover_image = _safe_str(row.get("Cover image"))
        for i in range(1, 9):
            col = f"Item Image {i}"
            if col in row.index:
                p.images[i - 1] = _safe_str(row.get(col))
        p.size_chart_template = _safe_str(row.get("Size Chart Template"))
        p.size_chart_image = _safe_str(row.get("Size Chart Image"))
        p.variation_name1 = _safe_str(row.get("Variation Name1"))

        # Parse variation option images (up to 3 options in media export)
        options_images = []
        for i in range(1, 4):
            opt_name = _safe_str(row.get(f"Option {i} Name"))
            opt_img = _safe_str(row.get(f"Option {i} Image"))
            if opt_name is not None or opt_img is not None:
                options_images.append((opt_name, opt_img))
        p.variation_options_images = options_images
        if p.parent_sku is None:
            p.parent_sku = _safe_str(row.get("Parent SKU"))


def _parse_sales_info(products: dict[float, Product], df: pd.DataFrame) -> None:
    """Merge sales_info data into products dict. Creates/updates variations."""
    for _, row in df.iterrows():
        pid = float(row["Product ID"])
        if pid not in products:
            products[pid] = Product(product_id=pid)
        p = products[pid]

        # Product-level fields (take from first row for this product)
        if p.min_purchase_qty is None:
            p.min_purchase_qty = _safe_str(row.get("Minimum Purchase Quantity"))
        if p.max_purchase_qty is None:
            p.max_purchase_qty = _safe_str(row.get("Maximum Purchase Quantity"))
            p.max_purchase_qty_start_date = _safe_str(
                row.get("Maximum Purchase Quantity - Start Date")
            )
            p.max_purchase_qty_time_period = _safe_str(
                row.get("Maximum Purchase Quantity - Time Period (in Days)")
            )
            p.max_purchase_qty_end_date = _safe_str(
                row.get("Maximum Purchase Quantity - End Date")
            )
        if p.parent_sku is None:
            p.parent_sku = _safe_str(row.get("Parent SKU"))

        # Variation-level
        var = Variation(
            variation_id=row.get("Variation ID") if pd.notna(row.get("Variation ID")) else None,
            name=_safe_str(row.get("Variation Name")),
            sku=_safe_str(row.get("SKU")),
            price=_safe_str(row.get("Price")),
            stock=_safe_str(row.get("Stock")),
        )
        p.variations.append(var)


def _parse_shipping_info(products: dict[float, Product], df: pd.DataFrame) -> None:
    """Merge shipping_info data into products dict."""
    for _, row in df.iterrows():
        pid = float(row["Product ID"])
        if pid not in products:
            products[pid] = Product(product_id=pid)
        p = products[pid]

        # Product-level weight/dimensions (take from first row)
        if p.weight_kg is None:
            p.weight_kg = _safe_str(row.get("Product Weight/kg"))
            p.length = _safe_str(row.get("Length"))
            p.width = _safe_str(row.get("Width"))
            p.height = _safe_str(row.get("Height"))

        # Update matching variation's weight if per-variation
        vid = row.get("Variation ID")
        if pd.notna(vid):
            vid_int = int(vid)
            for var in p.variations:
                if var.variation_id is not None and int(var.variation_id) == vid_int:
                    var.weight_kg = _safe_str(row.get("Product Weight/kg"))
                    var.length = _safe_str(row.get("Length"))
                    var.width = _safe_str(row.get("Width"))
                    var.height = _safe_str(row.get("Height"))
                    break


def _parse_dts_info(products: dict[float, Product], df: pd.DataFrame) -> None:
    """Merge dts_info data into products dict."""
    for _, row in df.iterrows():
        pid = float(row["Product ID"])
        if pid not in products:
            products[pid] = Product(product_id=pid)
        p = products[pid]

        if p.days_to_ship is None:
            p.days_to_ship = _safe_str(row.get("Days to ship"))
            p.non_preorder_dts = row.get("Non Pre-order DTS") if pd.notna(row.get("Non Pre-order DTS")) else None
            p.preorder_dts_range = _safe_str(row.get("Pre-order DTS Range"))

        # Also fill category from dts_info if not already set from media_info
        if p.category_raw is None:
            p.category_raw = _safe_str(row.get("Category"))
            if p.category_raw:
                parts = p.category_raw.split(" - ", 1)
                p.category_id = parts[0].strip() if parts else None

        # Per-variation DTS
        vid = row.get("Variation ID")
        if pd.notna(vid):
            vid_int = int(vid)
            for var in p.variations:
                if var.variation_id is not None and int(var.variation_id) == vid_int:
                    var.days_to_ship = _safe_str(row.get("Days to ship"))
                    break


_PARSERS = {
    "basic_info": _parse_basic_info,
    "media_info": _parse_media_info,
    "sales_info": _parse_sales_info,
    "shipping_info": _parse_shipping_info,
    "dts_info": _parse_dts_info,
}


def read_and_merge_exports(
    file_paths: list[str | Path],
) -> list[Product]:
    """Read multiple export files and merge them into a list of Product objects.

    Args:
        file_paths: Paths to the 5 export xlsx files (in any order).

    Returns:
        List of Product objects with all data merged by Product ID.
    """
    products: dict[float, Product] = {}

    # Parse in a specific order: basic_info first (establishes products),
    # then media_info, sales_info, shipping_info, dts_info
    parse_order = ["basic_info", "media_info", "sales_info", "shipping_info", "dts_info"]
    typed_files: dict[str, tuple[str | Path, pd.DataFrame]] = {}

    for path in file_paths:
        export_type, df = read_export(path)
        typed_files[export_type] = (path, df)

    for etype in parse_order:
        if etype in typed_files:
            _, df = typed_files[etype]
            _PARSERS[etype](products, df)

    return list(products.values())
