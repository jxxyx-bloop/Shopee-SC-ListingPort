"""Tests for the upload file writer."""

from pathlib import Path

import pandas as pd
import pytest

from shopee_transfer.mapper import transform_products
from shopee_transfer.models import TransformConfig
from shopee_transfer.reader import read_and_merge_exports
from shopee_transfer.writer import read_template_columns, write_upload_file

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
TEMPLATE = SAMPLES_DIR / "Shopee_mass_upload_2026-04-05_basic_template.xlsx"

ALL_EXPORTS = [
    SAMPLES_DIR / "mass_update_basic_info_2051980_20260405231315.xlsx",
    SAMPLES_DIR / "mass_update_sales_info_2051980_20260405231511.xlsx",
    SAMPLES_DIR / "mass_update_shipping_info_2051980_20260405231549.xlsx",
    SAMPLES_DIR / "mass_update_dts_info_2051980_20260405231621.xlsx",
    SAMPLES_DIR / "mass_update_media_info_2051980_20260405231634.xlsx",
]


class TestReadTemplateColumns:
    def test_reads_columns(self):
        cols = read_template_columns(TEMPLATE)
        assert len(cols) > 0
        assert "Product Name" in cols
        assert "Price" in cols
        assert "Weight" in cols

    def test_column_count(self):
        cols = read_template_columns(TEMPLATE)
        assert len(cols) == 43  # Known from analysis


class TestWriteUploadFile:
    def test_writes_file(self, tmp_path):
        products = read_and_merge_exports(ALL_EXPORTS)
        config = TransformConfig(
            source_market="my", target_market="sg", exchange_rate=0.29
        )
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        output = tmp_path / "test_output.xlsx"
        result = write_upload_file(rows, TEMPLATE, output)
        assert result.exists()
        assert result.stat().st_size > 0

    def test_output_preserves_header_rows(self, tmp_path):
        """Output should preserve the template's 5 header rows."""
        products = read_and_merge_exports(ALL_EXPORTS)
        config = TransformConfig(
            source_market="my", target_market="sg", exchange_rate=0.29
        )
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        output = tmp_path / "test_output.xlsx"
        write_upload_file(rows, TEMPLATE, output)

        # Read back and verify header structure
        df = pd.read_excel(output, engine="calamine", sheet_name="Template", header=None)
        # Row 0 should have internal field IDs
        assert "ps_product_name" in str(df.iloc[0, 1])
        # Row 2 should have human-readable column names
        assert df.iloc[2, 1] == "Product Name"

    def test_output_has_data_rows(self, tmp_path):
        """Output should have data starting at row 5 (0-indexed)."""
        products = read_and_merge_exports(ALL_EXPORTS)
        config = TransformConfig(
            source_market="my", target_market="sg", exchange_rate=0.29
        )
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        output = tmp_path / "test_output.xlsx"
        write_upload_file(rows, TEMPLATE, output)

        df = pd.read_excel(output, engine="calamine", sheet_name="Template", header=None)
        # Should have 5 header rows + data rows
        assert df.shape[0] >= 5 + len(rows)

    def test_output_file_size_under_3mb(self, tmp_path):
        """Upload file must be under 3MB."""
        products = read_and_merge_exports(ALL_EXPORTS)
        config = TransformConfig(
            source_market="my", target_market="sg", exchange_rate=0.29
        )
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        output = tmp_path / "test_output.xlsx"
        write_upload_file(rows, TEMPLATE, output)
        assert output.stat().st_size < 3 * 1024 * 1024  # 3MB
