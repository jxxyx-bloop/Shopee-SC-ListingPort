"""Configuration loading for market settings and category mappings."""

from __future__ import annotations

import json
from pathlib import Path

from .models import MarketConfig

# Default config directory — check relative to package, then cwd
def _find_default_config_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parent.parent.parent / "config",
        Path.cwd() / "config",
    ]
    for c in candidates:
        if (c / "markets.json").exists():
            return c
    return candidates[0]  # Fall back to first option


_DEFAULT_CONFIG_DIR = _find_default_config_dir()


def load_market_config(market_code: str, config_dir: Path | None = None) -> MarketConfig:
    """Load market configuration from markets.json."""
    config_dir = config_dir or _DEFAULT_CONFIG_DIR
    markets_file = config_dir / "markets.json"
    if not markets_file.exists():
        raise FileNotFoundError(f"Markets config not found: {markets_file}")

    with open(markets_file) as f:
        markets = json.load(f)

    if market_code not in markets:
        available = ", ".join(markets.keys())
        raise ValueError(f"Unknown market '{market_code}'. Available: {available}")

    return MarketConfig(**markets[market_code])


def load_category_mapping(
    source_market: str, target_market: str, config_dir: Path | None = None
) -> dict[str, str]:
    """Load category ID mapping from source market to target market.

    Returns a dict mapping source category ID (str) to target category ID (str).
    Empty string values mean "unmapped" — the seller needs to fill these in.
    """
    config_dir = config_dir or _DEFAULT_CONFIG_DIR
    mapping_file = config_dir / "category_mappings" / f"{source_market}_to_{target_market}.json"

    if not mapping_file.exists():
        return {}

    with open(mapping_file) as f:
        data = json.load(f)

    # Filter out comment keys (starting with _)
    return {k: v for k, v in data.items() if not k.startswith("_")}
