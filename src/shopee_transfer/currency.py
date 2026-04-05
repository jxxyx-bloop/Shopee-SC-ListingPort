"""Currency conversion for cross-market pricing."""

from __future__ import annotations

# Static exchange rates (source currency -> target currency)
# These are approximate rates — sellers should verify and override as needed.
STATIC_RATES: dict[tuple[str, str], float] = {
    ("MYR", "SGD"): 0.29,
    ("SGD", "MYR"): 3.45,
    ("MYR", "THB"): 7.80,
    ("SGD", "THB"): 26.90,
    ("MYR", "PHP"): 12.50,
    ("SGD", "PHP"): 43.10,
}


def convert_price(
    price_str: str,
    source_currency: str,
    target_currency: str,
    exchange_rate: float | None = None,
) -> str:
    """Convert a price string from source currency to target currency.

    Args:
        price_str: Price as string (e.g., "120.00")
        source_currency: Source currency code (e.g., "MYR")
        target_currency: Target currency code (e.g., "SGD")
        exchange_rate: Optional override rate. If None, uses static rates.

    Returns:
        Converted price as string with 2 decimal places.
    """
    if source_currency == target_currency:
        return price_str

    try:
        price = float(price_str)
    except (ValueError, TypeError):
        return price_str  # Return as-is if not a valid number

    if exchange_rate is None:
        key = (source_currency.upper(), target_currency.upper())
        if key not in STATIC_RATES:
            raise ValueError(
                f"No exchange rate for {source_currency} -> {target_currency}. "
                f"Provide --exchange-rate explicitly."
            )
        exchange_rate = STATIC_RATES[key]

    converted = price * exchange_rate
    return f"{converted:.2f}"
