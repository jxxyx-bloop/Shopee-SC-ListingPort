"""Tests for the export file reader."""

from pathlib import Path

import pytest

from shopee_transfer.reader import detect_export_type, read_and_merge_exports, read_export

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"

BASIC_INFO = SAMPLES_DIR / "mass_update_basic_info_2051980_20260405231315.xlsx"
SALES_INFO = SAMPLES_DIR / "mass_update_sales_info_2051980_20260405231511.xlsx"
SHIPPING_INFO = SAMPLES_DIR / "mass_update_shipping_info_2051980_20260405231549.xlsx"
DTS_INFO = SAMPLES_DIR / "mass_update_dts_info_2051980_20260405231621.xlsx"
MEDIA_INFO = SAMPLES_DIR / "mass_update_media_info_2051980_20260405231634.xlsx"

ALL_EXPORTS = [BASIC_INFO, SALES_INFO, SHIPPING_INFO, DTS_INFO, MEDIA_INFO]


class TestDetectExportType:
    def test_basic_info(self):
        assert detect_export_type(BASIC_INFO) == "basic_info"

    def test_sales_info(self):
        assert detect_export_type(SALES_INFO) == "sales_info"

    def test_shipping_info(self):
        assert detect_export_type(SHIPPING_INFO) == "shipping_info"

    def test_dts_info(self):
        assert detect_export_type(DTS_INFO) == "dts_info"

    def test_media_info(self):
        assert detect_export_type(MEDIA_INFO) == "media_info"


class TestReadExport:
    def test_basic_info_columns(self):
        etype, df = read_export(BASIC_INFO)
        assert etype == "basic_info"
        assert "Product ID" in df.columns
        assert "Product Name" in df.columns
        assert "Product Description" in df.columns
        assert len(df) > 0

    def test_sales_info_has_variations(self):
        etype, df = read_export(SALES_INFO)
        assert etype == "sales_info"
        assert "Variation ID" in df.columns
        assert "Price" in df.columns
        assert "Stock" in df.columns
        # Should have more rows than unique products (due to variations)
        unique_products = df["Product ID"].nunique()
        assert len(df) >= unique_products

    def test_media_info_has_images(self):
        etype, df = read_export(MEDIA_INFO)
        assert etype == "media_info"
        assert "Cover image" in df.columns
        assert "Item Image 1" in df.columns

    def test_shipping_info_has_weight(self):
        etype, df = read_export(SHIPPING_INFO)
        assert etype == "shipping_info"
        assert "Product Weight/kg" in df.columns

    def test_no_instruction_rows_in_data(self):
        """Ensure instruction/header rows are filtered out."""
        _, df = read_export(SALES_INFO)
        # All Product IDs should be numeric
        for pid in df["Product ID"]:
            assert isinstance(pid, (int, float))
            assert pid > 0


class TestMergeExports:
    def test_merge_all_five(self):
        products = read_and_merge_exports(ALL_EXPORTS)
        assert len(products) > 0

    def test_products_have_basic_info(self):
        products = read_and_merge_exports(ALL_EXPORTS)
        for p in products:
            assert p.product_id > 0
            assert p.name is not None

    def test_products_have_images(self):
        products = read_and_merge_exports(ALL_EXPORTS)
        products_with_images = [p for p in products if p.cover_image is not None]
        assert len(products_with_images) > 0
        # Check image URLs look valid
        for p in products_with_images:
            assert p.cover_image.startswith("https://")

    def test_products_have_variations(self):
        products = read_and_merge_exports(ALL_EXPORTS)
        multi_var = [p for p in products if p.has_variations]
        assert len(multi_var) > 0
        for p in multi_var:
            assert len(p.variations) >= 2
            for v in p.variations:
                assert v.price is not None

    def test_products_have_weight(self):
        products = read_and_merge_exports(ALL_EXPORTS)
        products_with_weight = [p for p in products if p.weight_kg is not None]
        assert len(products_with_weight) > 0

    def test_products_have_category(self):
        products = read_and_merge_exports(ALL_EXPORTS)
        products_with_cat = [p for p in products if p.category_id is not None]
        assert len(products_with_cat) > 0
