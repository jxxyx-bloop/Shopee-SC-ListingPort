"""Streamlit web app for Shopee cross-market listing transfer."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import streamlit as st

from shopee_transfer.config import load_market_config
from shopee_transfer.currency import STATIC_RATES
from shopee_transfer.mapper import transform_products
from shopee_transfer.models import TransformConfig
from shopee_transfer.reader import detect_export_type, read_and_merge_exports
from shopee_transfer.writer import write_upload_file

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "config"
MARKETS_FILE = CONFIG_DIR / "markets.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_markets() -> dict:
    """Load available markets from config."""
    with open(MARKETS_FILE) as f:
        return json.load(f)


def _get_default_rate(source_currency: str, target_currency: str) -> float:
    """Get default exchange rate or return 1.0."""
    return STATIC_RATES.get((source_currency, target_currency), 1.0)


def _save_uploaded_file(uploaded_file, cache_key: str) -> Path:
    """Save a Streamlit UploadedFile to a temp file and return its path.

    Uses session_state to cache the path so we don't create a new temp file
    on every Streamlit rerun. Old temp files are cleaned up when replaced.
    """
    state_key = f"_tmp_path_{cache_key}"

    # Check if we already saved this exact file (same name + size)
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    id_key = f"_tmp_id_{cache_key}"
    if state_key in st.session_state and id_key in st.session_state:
        if st.session_state[id_key] == file_id:
            existing = Path(st.session_state[state_key])
            if existing.exists():
                return existing

    # Clean up old temp file if it exists
    if state_key in st.session_state:
        old_path = Path(st.session_state[state_key])
        old_path.unlink(missing_ok=True)

    suffix = Path(uploaded_file.name).suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded_file.getvalue())
    tmp.close()
    st.session_state[state_key] = tmp.name
    st.session_state[id_key] = file_id
    return Path(tmp.name)


def _detect_type_safe(path: Path) -> str | None:
    """Detect export type, returning None on failure."""
    try:
        return detect_export_type(path)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Shopee Listing Transfer",
    page_icon="🛒",
    layout="wide",
)

st.title("Shopee Cross-Market Listing Transfer")
st.caption(
    "Transform product listings exported from one Shopee market into the "
    "upload format for another market."
)

# ---------------------------------------------------------------------------
# Step 1: Market Configuration
# ---------------------------------------------------------------------------

st.header("Step 1: Configure Markets")

markets = _load_markets()
market_codes = list(markets.keys())
market_labels = {code: f"{code.upper()} ({markets[code]['currency']})" for code in market_codes}

col1, col2, col3 = st.columns(3)

with col1:
    source_market = st.selectbox(
        "Source Market",
        market_codes,
        format_func=lambda c: market_labels[c],
        index=0,
    )

with col2:
    # Default target to the other market
    default_target = 1 if source_market == market_codes[0] else 0
    target_market = st.selectbox(
        "Target Market",
        market_codes,
        format_func=lambda c: market_labels[c],
        index=default_target,
    )

if source_market == target_market:
    st.error("Source and target markets must be different.")
    st.stop()

source_cfg = load_market_config(source_market, CONFIG_DIR)
target_cfg = load_market_config(target_market, CONFIG_DIR)
default_rate = _get_default_rate(source_cfg.currency, target_cfg.currency)

with col3:
    exchange_rate = st.number_input(
        f"Exchange Rate ({source_cfg.currency} → {target_cfg.currency})",
        min_value=0.0001,
        value=default_rate,
        step=0.01,
        format="%.4f",
    )

st.divider()

# ---------------------------------------------------------------------------
# Step 2: Upload Files
# ---------------------------------------------------------------------------

st.header("Step 2: Upload Files")

st.subheader("Export Files (from source market)")
st.caption(
    f"Upload the 5 Mass Update export files from your **{source_market.upper()}** Seller Center. "
    "Each file is auto-verified."
)

EXPORT_LABELS = {
    "basic_info": ("Basic Info", "mass_update_basic_info_*.xlsx"),
    "sales_info": ("Sales Info", "mass_update_sales_info_*.xlsx"),
    "shipping_info": ("Shipping Info", "mass_update_shipping_info_*.xlsx"),
    "dts_info": ("Days to Ship", "mass_update_dts_info_*.xlsx"),
    "media_info": ("Media / Images", "mass_update_media_info_*.xlsx"),
}

uploaded_exports: dict[str, Path] = {}
export_cols = st.columns(5)

for i, (expected_type, (label, hint)) in enumerate(EXPORT_LABELS.items()):
    with export_cols[i]:
        uploaded = st.file_uploader(
            label,
            type=["xlsx"],
            key=f"export_{expected_type}",
            help=f"Expected file: {hint}",
        )
        if uploaded:
            tmp_path = _save_uploaded_file(uploaded, f"export_{expected_type}")
            detected = _detect_type_safe(tmp_path)
            if detected == expected_type:
                st.success(f"{detected}", icon="✅")
                uploaded_exports[expected_type] = tmp_path
            elif detected:
                st.warning(f"Got: {detected}", icon="⚠️")
                uploaded_exports[detected] = tmp_path
            else:
                st.error("Unrecognized file", icon="❌")

st.subheader("Upload Template (for target market)")
st.caption(
    f"Upload the Mass Upload **Basic Template** downloaded from your **{target_market.upper()}** Seller Center."
)

template_file = st.file_uploader(
    "Upload Template (.xlsx)",
    type=["xlsx"],
    key="upload_template",
    help="Download from: Mass Upload > Download Template > Basic Template",
)

template_path: Path | None = None
if template_file:
    template_path = _save_uploaded_file(template_file, "upload_template")
    st.success("Template uploaded", icon="✅")

# Check readiness
all_exports_ready = len(uploaded_exports) == 5
template_ready = template_path is not None

if not all_exports_ready:
    missing = set(EXPORT_LABELS.keys()) - set(uploaded_exports.keys())
    st.info(f"Waiting for: {', '.join(EXPORT_LABELS[m][0] for m in missing)}")

if not template_ready:
    st.info("Waiting for upload template")

if not (all_exports_ready and template_ready):
    st.stop()

st.divider()

# ---------------------------------------------------------------------------
# Step 3: Review & Map Categories
# ---------------------------------------------------------------------------

st.header("Step 3: Review & Map Categories")

# Parse all exports (cached to avoid re-parsing on every widget interaction)
@st.cache_data
def _parse_exports(paths: tuple[str, ...]) -> list:
    return read_and_merge_exports([Path(p) for p in paths])

with st.spinner("Parsing export files..."):
    export_paths = tuple(str(uploaded_exports[t]) for t in EXPORT_LABELS.keys())
    products = _parse_exports(export_paths)

# Summary metrics
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
total_products = len(products)
products_with_vars = sum(1 for p in products if p.has_variations)
total_variations = sum(max(1, len(p.variations)) for p in products)
products_with_images = sum(1 for p in products if p.cover_image)

col_m1.metric("Total Products", total_products)
col_m2.metric("With Variations", products_with_vars)
col_m3.metric("Total Upload Rows", total_variations)
col_m4.metric("With Images", products_with_images)

# Product preview table
st.subheader("Product Preview")
preview_data = []
for p in products:
    first_price = p.variations[0].price if p.variations else "N/A"
    preview_data.append({
        "Product Name": p.name or "(unnamed)",
        "Category": p.category_raw or "(none)",
        "Price (source)": first_price,
        "Variations": len(p.variations),
        "Has Images": "Yes" if p.cover_image else "No",
    })

st.dataframe(preview_data, use_container_width=True, height=300)

# Category mapping
st.subheader("Category Mapping")
st.caption(
    f"Map source ({source_market.upper()}) category IDs to target ({target_market.upper()}) category IDs. "
    "Leave blank to keep the source ID (you can fix it in the upload file later)."
)

# Extract unique categories
unique_categories: dict[str, str] = {}
for p in products:
    if p.category_id and p.category_id not in unique_categories:
        unique_categories[p.category_id] = p.category_raw or p.category_id

if not unique_categories:
    st.info("No categories found in export data.")
else:
    # Initialize session state for category mappings
    if "cat_mappings" not in st.session_state:
        st.session_state.cat_mappings = {}

    cat_cols = st.columns(2)
    cat_items = list(unique_categories.items())

    for i, (cat_id, cat_display) in enumerate(cat_items):
        col = cat_cols[i % 2]
        with col:
            mapped_value = st.text_input(
                f"{cat_display}",
                value=st.session_state.cat_mappings.get(cat_id, ""),
                key=f"cat_{cat_id}",
                placeholder=f"Target {target_market.upper()} category ID",
            )
            st.session_state.cat_mappings[cat_id] = mapped_value

# Currency preview
st.subheader("Price Conversion Preview")
preview_prices = []
for p in products[:5]:
    if p.variations and p.variations[0].price:
        src_price = p.variations[0].price
        try:
            converted = float(src_price) * exchange_rate
            preview_prices.append({
                "Product": p.name or "(unnamed)",
                f"Price ({source_cfg.currency})": src_price,
                f"Price ({target_cfg.currency})": f"{converted:.2f}",
            })
        except (ValueError, TypeError):
            pass

if preview_prices:
    st.dataframe(preview_prices, use_container_width=True)
else:
    st.info("No prices available for preview.")

st.divider()

# ---------------------------------------------------------------------------
# Step 4: Transform & Download
# ---------------------------------------------------------------------------

st.header("Step 4: Transform & Download")

if st.button("Generate Upload File", type="primary", use_container_width=True):
    with st.spinner("Transforming listings..."):
        # Build category overrides from session state
        category_overrides = {
            k: v for k, v in st.session_state.get("cat_mappings", {}).items() if v.strip()
        }

        transform_config = TransformConfig(
            source_market=source_market,
            target_market=target_market,
            exchange_rate=exchange_rate,
        )

        try:
            rows = transform_products(
                products,
                transform_config,
                config_dir=CONFIG_DIR,
                category_overrides=category_overrides if category_overrides else None,
            )

            # Write to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_out:
                output_path = Path(tmp_out.name)

            write_upload_file(rows, template_path, output_path)

            # Read back for download
            with open(output_path, "rb") as f:
                output_bytes = f.read()

            # Summary
            file_size_kb = len(output_bytes) / 1024
            st.success(
                f"Generated upload file: **{total_products} products** → "
                f"**{len(rows)} rows** ({file_size_kb:.0f} KB)"
            )

            if file_size_kb > 3072:
                st.warning(
                    "File exceeds 3MB limit! Consider splitting into multiple files.",
                    icon="⚠️",
                )

            output_filename = (
                f"upload_{source_market}_to_{target_market}.xlsx"
            )
            st.download_button(
                label=f"Download {output_filename}",
                data=output_bytes,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
            )

            # Cleanup
            output_path.unlink(missing_ok=True)

        except Exception as e:
            st.error(f"Transformation failed: {e}")
            st.exception(e)

# Footer
st.divider()
st.caption(
    "Shopee Cross-Market Listing Transfer Tool v0.1 | "
    f"Source: {source_market.upper()} ({source_cfg.currency}) → "
    f"Target: {target_market.upper()} ({target_cfg.currency})"
)
