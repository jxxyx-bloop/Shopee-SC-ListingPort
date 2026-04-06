# Shopee Cross-Market Listing Transfer Tool

A tool that helps Shopee sellers transfer product listings from one market's Seller Center to another (e.g., Malaysia to Singapore). It reads Mass Update export files, transforms the data, and generates a ready-to-upload Mass Upload file for the target market.

Built to support **Cross-Border (CB) merchants** who maintain accounts across multiple Shopee markets but lack a Global Seller Center.

## How It Works

```
Source Market (MY)                    Target Market (SG)
Seller Center                        Seller Center
Mass Update > Download               Mass Upload > Upload File
        |                                    ^
        v                                    |
 5 Export Files ──> [This Tool] ──> Upload-ready .xlsx
  basic_info          - Merge by Product ID
  sales_info          - Convert currency
  shipping_info       - Map categories
  dts_info            - Restructure variations
  media_info          - Preserve template format
```

## Quick Start

### Prerequisites

- Python 3.10+
- 5 Mass Update export files from the source market
- 1 Mass Upload Basic Template from the target market

### Installation

```bash
pip install -e ".[dev,web]"
```

### Option 1: CLI

```bash
shopee-transfer convert \
  --source my --target sg \
  --basic-info samples/mass_update_basic_info_*.xlsx \
  --sales-info samples/mass_update_sales_info_*.xlsx \
  --shipping-info samples/mass_update_shipping_info_*.xlsx \
  --dts-info samples/mass_update_dts_info_*.xlsx \
  --media-info samples/mass_update_media_info_*.xlsx \
  --template samples/Shopee_mass_upload_*_basic_template.xlsx \
  --exchange-rate 0.29 \
  --output upload_ready.xlsx
```

### Option 2: Web App (Streamlit)

```bash
streamlit run src/shopee_transfer/web/app.py
```

Then open `http://localhost:8501` in your browser. The web app provides:
1. Market selection and exchange rate configuration
2. Drag-and-drop file upload with auto-detection
3. Product preview table and interactive category mapping
4. One-click transform and download

## What Gets Transferred

| Data | Source Export | Handling |
|---|---|---|
| Product Name & Description | basic_info | Direct copy |
| Price & Stock | sales_info | Price converted using exchange rate |
| Weight & Dimensions | shipping_info | Direct copy |
| Images (cover + 8) | media_info | URL passthrough (shared CDN) |
| Category | media_info / dts_info | Mapped via config or manual input |
| Variations (color, size) | sales_info + media_info | Restructured to upload format |
| Days to Ship | dts_info | Direct copy |
| Purchase Qty Limits | sales_info | Direct copy |
| Shipping Channels | shipping_info | **Not mapped** (differs per market, defaults to "On") |

## Project Structure

```
ShopeeSC/
  pyproject.toml                  # Project config and dependencies
  config/
    markets.json                  # Market configs (currency, shipping channels)
    category_mappings/
      my_to_sg.json               # Category ID mapping (MY -> SG)
  samples/                        # Sample export and template files
  src/shopee_transfer/
    models.py                     # Pydantic data models (Product, Variation, etc.)
    reader.py                     # Parse 5 export files, merge by Product ID
    mapper.py                     # Column mapping, currency conversion, variation restructuring
    writer.py                     # Generate upload xlsx preserving template headers
    currency.py                   # Currency conversion with static/custom rates
    config.py                     # Load market configs and category mappings
    cli.py                        # Click CLI entry point
    web/
      app.py                      # Streamlit web app
  tests/                          # 60 tests covering all modules
```

## Configuration

### Exchange Rates

Built-in static rates (override via `--exchange-rate` or the web UI):

| Pair | Rate |
|---|---|
| MYR -> SGD | 0.29 |
| SGD -> MYR | 3.45 |
| MYR -> THB | 7.80 |
| MYR -> PHP | 12.50 |

### Category Mapping

Category IDs differ between markets. Edit `config/category_mappings/my_to_sg.json` to add mappings:

```json
{
  "101379": "200345",
  "100226": "100226"
}
```

Or use the web app's interactive category mapping UI to set them per-session.

### Adding New Markets

Add entries to `config/markets.json`:

```json
{
  "th": {
    "code": "th",
    "currency": "THB",
    "tld": "co.th",
    "shipping_channels": ["..."],
    "direct_listing_price_column": null
  }
}
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## After Generating the Upload File

1. Open the output `.xlsx` and review the data
2. Fill in any unmapped category IDs for the target market
3. Verify prices after currency conversion
4. Upload to the target market's Seller Center: **My Products > Mass Function > Mass Upload > Upload File**

## Limitations

- Shipping channels cannot be auto-mapped between markets (different channel sets per market)
- Category mapping requires manual setup per market pair
- Upload file must be under 3MB / ~500 products (Shopee limit)
- Shopee-generated xlsx files require the `calamine` engine to read (openpyxl compatibility issue)
