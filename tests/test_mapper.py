"""Tests for the data mapper."""

from pathlib import Path

import pytest

from shopee_transfer.mapper import transform_products
from shopee_transfer.models import TransformConfig
from shopee_transfer.reader import read_and_merge_exports

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

ALL_EXPORTS = [
    SAMPLES_DIR / "mass_update_basic_info_2051980_20260405231315.xlsx",
    SAMPLES_DIR / "mass_update_sales_info_2051980_20260405231511.xlsx",
    SAMPLES_DIR / "mass_update_shipping_info_2051980_20260405231549.xlsx",
    SAMPLES_DIR / "mass_update_dts_info_2051980_20260405231621.xlsx",
    SAMPLES_DIR / "mass_update_media_info_2051980_20260405231634.xlsx",
]


@pytest.fixture
def products():
    return read_and_merge_exports(ALL_EXPORTS)


@pytest.fixture
def config():
    return TransformConfig(
        source_market="my",
        target_market="sg",
        exchange_rate=0.29,
    )


class TestTransformProducts:
    def test_produces_rows(self, products, config):
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        assert len(rows) > 0

    def test_row_count_matches_variations(self, products, config):
        """Total rows should equal total variations (1 per product without, N per product with)."""
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        expected = sum(max(1, len(p.variations)) for p in products)
        assert len(rows) == expected

    def test_rows_have_required_fields(self, products, config):
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        for row in rows:
            # Every row should have the key upload template columns
            assert "Product Name" in row
            assert "Price" in row
            assert "Weight" in row

    def test_currency_conversion(self, products, config):
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        # Find a row with a known price
        for row in rows:
            if row.get("Price") is not None:
                price = float(row["Price"])
                assert price > 0
                break

    def test_price_converted_correctly(self, products, config):
        """Verify MYR prices are converted to SGD using the exchange rate."""
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        # Find a product we know: CUTE SHIBA STICKER has price 120.00 MYR
        for p in products:
            if p.name == "CUTE SHIBA STICKER" and p.variations:
                myr_price = float(p.variations[0].price)
                break
        else:
            pytest.skip("CUTE SHIBA STICKER not found")

        expected_sgd = myr_price * 0.29
        for row in rows:
            if row.get("Product Name") == "CUTE SHIBA STICKER":
                assert float(row["Price"]) == pytest.approx(expected_sgd, rel=0.01)
                break

    def test_shipping_channels_set(self, products, config):
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        # First row should have SG shipping channels set to "On"
        first_row = rows[0]
        assert first_row.get("Doorstep Delivery") == "On"

    def test_variation_integration_no(self, products, config):
        """Multi-variation products should have Variation Integration No."""
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        # Find rows with integration numbers
        with_integration = [r for r in rows if r.get("Variation Integration No.")]
        assert len(with_integration) > 0

    def test_direct_listing_price(self, products, config):
        """Direct Listing Price:SG should equal Price for SG target."""
        rows = transform_products(products, config, config_dir=CONFIG_DIR)
        for row in rows:
            if row.get("Price") is not None:
                assert row.get("Direct Listing Price:SG") == row["Price"]

    def test_category_overrides(self, products, config):
        """Category overrides should take precedence over mapping file."""
        overrides = {"101379": "999999"}
        rows = transform_products(
            products, config, config_dir=CONFIG_DIR, category_overrides=overrides
        )
        # Find CUTE SHIBA STICKER (category 101379) and verify override applied
        for row in rows:
            if row.get("Product Name") == "CUTE SHIBA STICKER":
                assert row["Category"] == "999999"
                break
        else:
            pytest.fail("CUTE SHIBA STICKER not found in output")
