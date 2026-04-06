"""Tests for the Streamlit web app helpers and end-to-end flow."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from shopee_transfer.config import load_market_config
from shopee_transfer.currency import STATIC_RATES
from shopee_transfer.mapper import transform_products
from shopee_transfer.models import TransformConfig
from shopee_transfer.reader import detect_export_type, read_and_merge_exports
from shopee_transfer.writer import read_template_columns, write_upload_file

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

BASIC_INFO = SAMPLES_DIR / "mass_update_basic_info_2051980_20260405231315.xlsx"
SALES_INFO = SAMPLES_DIR / "mass_update_sales_info_2051980_20260405231511.xlsx"
SHIPPING_INFO = SAMPLES_DIR / "mass_update_shipping_info_2051980_20260405231549.xlsx"
DTS_INFO = SAMPLES_DIR / "mass_update_dts_info_2051980_20260405231621.xlsx"
MEDIA_INFO = SAMPLES_DIR / "mass_update_media_info_2051980_20260405231634.xlsx"
TEMPLATE = SAMPLES_DIR / "Shopee_mass_upload_2026-04-05_basic_template.xlsx"

ALL_EXPORTS = [BASIC_INFO, SALES_INFO, SHIPPING_INFO, DTS_INFO, MEDIA_INFO]


class TestWebAppHelpers:
    """Test the helper functions used by the web app."""

    def test_load_markets_json(self):
        """Verify markets.json loads and has expected structure."""
        markets_file = CONFIG_DIR / "markets.json"
        with open(markets_file) as f:
            markets = json.load(f)
        assert "my" in markets
        assert "sg" in markets
        assert markets["my"]["currency"] == "MYR"
        assert markets["sg"]["currency"] == "SGD"

    def test_get_default_rate(self):
        """Verify static rates are available for MY -> SG."""
        rate = STATIC_RATES.get(("MYR", "SGD"), None)
        assert rate is not None
        assert rate == 0.29

    def test_get_default_rate_unknown_pair(self):
        """Unknown pair should return None from STATIC_RATES."""
        rate = STATIC_RATES.get(("USD", "EUR"), None)
        assert rate is None

    def test_detect_export_type_all_files(self):
        """Each sample file should be correctly detected."""
        expected = {
            BASIC_INFO: "basic_info",
            SALES_INFO: "sales_info",
            SHIPPING_INFO: "shipping_info",
            DTS_INFO: "dts_info",
            MEDIA_INFO: "media_info",
        }
        for path, expected_type in expected.items():
            assert detect_export_type(path) == expected_type

    def test_detect_export_type_rejects_template(self):
        """Upload template should NOT be detected as an export type."""
        with pytest.raises((ValueError, Exception)):
            detect_export_type(TEMPLATE)

    def test_config_dir_path(self):
        """Verify the CONFIG_DIR resolution used by the web app."""
        web_app_path = Path(__file__).resolve().parent.parent / "src" / "shopee_transfer" / "web"
        config_dir = web_app_path.parent.parent.parent / "config"
        assert config_dir.exists()
        assert (config_dir / "markets.json").exists()


class TestWebAppEndToEndFlow:
    """Simulate the full web app flow: upload -> parse -> transform -> download."""

    def test_step1_market_config(self):
        """Step 1: Load market configs and verify exchange rate available."""
        source_cfg = load_market_config("my", CONFIG_DIR)
        target_cfg = load_market_config("sg", CONFIG_DIR)

        assert source_cfg.currency == "MYR"
        assert target_cfg.currency == "SGD"
        assert target_cfg.direct_listing_price_column == "Direct Listing Price:SG"

        rate = STATIC_RATES.get((source_cfg.currency, target_cfg.currency))
        assert rate is not None

    def test_step2_parse_exports(self):
        """Step 2: Parse all 5 export files and verify product data."""
        products = read_and_merge_exports(ALL_EXPORTS)

        assert len(products) == 30
        products_with_vars = sum(1 for p in products if p.has_variations)
        assert products_with_vars == 8
        products_with_images = sum(1 for p in products if p.cover_image)
        assert products_with_images == 30

    def test_step3_category_extraction(self):
        """Step 3: Extract unique categories for mapping UI."""
        products = read_and_merge_exports(ALL_EXPORTS)

        unique_categories = {}
        for p in products:
            if p.category_id and p.category_id not in unique_categories:
                unique_categories[p.category_id] = p.category_raw or p.category_id

        assert len(unique_categories) > 0
        # All category IDs should be numeric strings
        for cat_id in unique_categories:
            assert cat_id.isdigit(), f"Category ID '{cat_id}' is not numeric"

    def test_step3_price_preview(self):
        """Step 3: Price conversion preview should produce valid numbers."""
        products = read_and_merge_exports(ALL_EXPORTS)
        exchange_rate = 0.29

        preview_prices = []
        for p in products[:5]:
            if p.variations and p.variations[0].price:
                src_price = p.variations[0].price
                try:
                    converted = float(src_price) * exchange_rate
                    preview_prices.append({
                        "Product": p.name,
                        "source": src_price,
                        "target": f"{converted:.2f}",
                    })
                except (ValueError, TypeError):
                    pass

        assert len(preview_prices) > 0
        for item in preview_prices:
            assert float(item["target"]) > 0

    def test_step4_transform_and_write(self, tmp_path):
        """Step 4: Full transform and write should produce valid output."""
        products = read_and_merge_exports(ALL_EXPORTS)

        # Simulate user category overrides from web UI
        category_overrides = {"101379": "200001"}

        config = TransformConfig(
            source_market="my",
            target_market="sg",
            exchange_rate=0.29,
        )

        rows = transform_products(
            products, config, config_dir=CONFIG_DIR,
            category_overrides=category_overrides,
        )

        assert len(rows) == 40  # 30 products + 10 extra variation rows

        # Write output
        output = tmp_path / "web_test_output.xlsx"
        write_upload_file(rows, TEMPLATE, output)

        assert output.exists()
        assert output.stat().st_size > 0
        assert output.stat().st_size < 3 * 1024 * 1024  # Under 3MB

    def test_step4_output_columns_match_template(self, tmp_path):
        """Output column headers must match the template exactly."""
        products = read_and_merge_exports(ALL_EXPORTS)
        config = TransformConfig(
            source_market="my", target_market="sg", exchange_rate=0.29
        )
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        output = tmp_path / "col_test.xlsx"
        write_upload_file(rows, TEMPLATE, output)

        # Read back column headers from output
        import pandas as pd
        df_out = pd.read_excel(output, engine="calamine", sheet_name="Template", header=None)
        df_tpl = pd.read_excel(TEMPLATE, engine="calamine", sheet_name="Template", header=None)

        # Row 2 should have identical column names
        out_headers = [str(v) if not pd.isna(v) else "" for v in df_out.iloc[2].tolist()]
        tpl_headers = [str(v) if not pd.isna(v) else "" for v in df_tpl.iloc[2].tolist()]
        assert out_headers == tpl_headers

    def test_step4_data_starts_at_correct_row(self, tmp_path):
        """Data should start at row 6 (1-indexed), after 5 header rows."""
        products = read_and_merge_exports(ALL_EXPORTS)
        config = TransformConfig(
            source_market="my", target_market="sg", exchange_rate=0.29
        )
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        output = tmp_path / "row_test.xlsx"
        write_upload_file(rows, TEMPLATE, output)

        import pandas as pd
        df = pd.read_excel(output, engine="calamine", sheet_name="Template", header=None)

        # Row 0: internal IDs, Row 1: metadata, Row 2: headers,
        # Row 3: mandatory/optional, Row 4: instructions
        # Row 5: first data row (0-indexed)
        first_data_val = df.iloc[5, 1]  # Product Name column
        assert first_data_val is not None and str(first_data_val) != "nan"

    def test_step4_variation_rows_structure(self, tmp_path):
        """Multi-variation products: first row has product info, subsequent rows don't."""
        products = read_and_merge_exports(ALL_EXPORTS)
        config = TransformConfig(
            source_market="my", target_market="sg", exchange_rate=0.29
        )
        rows = transform_products(products, config, config_dir=CONFIG_DIR)

        # Find a product with variations
        multi_var_products = [p for p in products if p.has_variations]
        assert len(multi_var_products) > 0

        # Find the rows for the first multi-var product
        target_product = multi_var_products[0]
        integration_nos = set()
        product_rows = []
        for row in rows:
            if row.get("Product Name") == target_product.name:
                product_rows.append(row)
                if row.get("Variation Integration No."):
                    integration_nos.add(row["Variation Integration No."])

        # First row should have the product name
        assert product_rows[0]["Product Name"] == target_product.name

        # Find continuation rows (same integration no, no product name)
        if integration_nos:
            int_no = list(integration_nos)[0]
            continuation_rows = [
                r for r in rows
                if r.get("Variation Integration No.") == int_no
                and r.get("Product Name") is None
            ]
            assert len(continuation_rows) > 0
            for r in continuation_rows:
                # Continuation rows should have variation-specific data
                assert r.get("Option for Variation 1") is not None
                assert r.get("Price") is not None

    def test_full_roundtrip_download_bytes(self, tmp_path):
        """Simulate the exact bytes-based download flow the web app uses."""
        products = read_and_merge_exports(ALL_EXPORTS)
        config = TransformConfig(
            source_market="my", target_market="sg", exchange_rate=0.29
        )
        rows = transform_products(products, config, config_dir=CONFIG_DIR)

        output = tmp_path / "download_test.xlsx"
        write_upload_file(rows, TEMPLATE, output)

        # Read back as bytes (this is what st.download_button receives)
        with open(output, "rb") as f:
            output_bytes = f.read()

        assert len(output_bytes) > 0
        file_size_kb = len(output_bytes) / 1024
        assert file_size_kb < 3072  # Under 3MB

        # Verify it's a valid xlsx by checking zip magic bytes
        assert output_bytes[:4] == b'PK\x03\x04'
