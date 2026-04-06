"""Tests for currency conversion."""

import pytest

from shopee_transfer.currency import convert_price


class TestConvertPrice:
    def test_basic_conversion(self):
        result = convert_price("100.00", "MYR", "SGD", exchange_rate=0.29)
        assert result == "29.00"

    def test_same_currency(self):
        result = convert_price("50.00", "SGD", "SGD")
        assert result == "50.00"

    def test_static_rate_fallback(self):
        result = convert_price("100.00", "MYR", "SGD")
        assert result == "29.00"

    def test_override_rate(self):
        result = convert_price("100.00", "MYR", "SGD", exchange_rate=0.30)
        assert result == "30.00"

    def test_invalid_price_returns_as_is(self):
        result = convert_price("not-a-number", "MYR", "SGD", exchange_rate=0.29)
        assert result == "not-a-number"

    def test_unknown_currency_pair_raises(self):
        with pytest.raises(ValueError, match="No exchange rate"):
            convert_price("100.00", "USD", "EUR")

    def test_two_decimal_places(self):
        result = convert_price("33.33", "MYR", "SGD", exchange_rate=0.29)
        assert result == "9.67"

    def test_zero_price(self):
        result = convert_price("0.00", "MYR", "SGD", exchange_rate=0.29)
        assert result == "0.00"
