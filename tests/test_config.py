"""Tests for configuration loading."""

from pathlib import Path

import pytest

from shopee_transfer.config import load_category_mapping, load_market_config

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


class TestLoadMarketConfig:
    def test_load_my(self):
        cfg = load_market_config("my", CONFIG_DIR)
        assert cfg.code == "my"
        assert cfg.currency == "MYR"
        assert len(cfg.shipping_channels) > 0

    def test_load_sg(self):
        cfg = load_market_config("sg", CONFIG_DIR)
        assert cfg.code == "sg"
        assert cfg.currency == "SGD"
        assert cfg.direct_listing_price_column == "Direct Listing Price:SG"

    def test_unknown_market_raises(self):
        with pytest.raises(ValueError, match="Unknown market"):
            load_market_config("xx", CONFIG_DIR)

    def test_missing_config_dir_raises(self):
        with pytest.raises(FileNotFoundError):
            load_market_config("my", Path("/nonexistent/dir"))


class TestLoadCategoryMapping:
    def test_load_my_to_sg(self):
        mapping = load_category_mapping("my", "sg", CONFIG_DIR)
        assert isinstance(mapping, dict)
        # Should not include comment keys
        assert "_comment" not in mapping
        assert "_example" not in mapping

    def test_nonexistent_mapping_returns_empty(self):
        mapping = load_category_mapping("xx", "yy", CONFIG_DIR)
        assert mapping == {}
