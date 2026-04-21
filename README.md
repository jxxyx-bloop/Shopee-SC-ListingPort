# Shopee Cross-Market Listing Transfer Tool

A tool that helps Shopee sellers copy product listings from one market's Seller Center to another (e.g., Malaysia → Singapore). It reads Mass Update export files, transforms the data, and generates a ready-to-upload Mass Upload file for the target market.

Useful for sellers who are **expanding into a new Shopee market** and need to migrate or duplicate an existing catalog — without having to re-enter every product by hand.

See feature pitch deck here: https://shopee-sc-listing-transfer.vercel.app/

---

## When Would You Need This?

When you operate stores in multiple Shopee markets, you'll occasionally need to replicate listings across them — for example when:

- Setting up a new storefront in a different market with an existing product catalog
- Running a market-expansion pilot with a curated subset of SKUs
- Keeping product information consistent across markets after a bulk update

This tool automates the file transformation between Shopee's Mass Update export format and Mass Upload import format, handling currency conversion, category remapping, and variation restructuring along the way.

---

## Better Long-Term: Shopee's Native Cross-Market Programs

If cross-market listing sync is a recurring need for your business, Shopee offers two official programs purpose-built for exactly this — with built-in sync, localisation support, and logistics handling that go well beyond what a file conversion tool can provide:

### Shopee International Platform (SIP)
SIP lets you sell your home-market listings to buyers in other Shopee markets directly from a single store. Shopee handles cross-border logistics, currency, and listing synchronisation across markets — so you don't need to manage separate storefronts at all.
[Learn more about SIP →](https://seller.shopee.sg/edu/article/21486)

### Shopee Direct Selling
Shopee's Direct Selling model lets you partner with Shopee as a supply partner, offloading fulfilment, operations, and cross-market distribution to Shopee directly. It's the simplest path to multi-market reach without the overhead of managing each market independently.
[Learn more about Direct Selling →](https://seller.shopee.sg/edu/article/26946)

> **Recommendation:** If you're regularly syncing listings across markets, evaluate SIP or Direct Selling first — they handle the complexity natively and provide ongoing automation. Use this tool for one-off migrations or situations where those programs aren't yet available for your market pair.

---

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

**Live App:** https://shopeesc-listingtransfer.streamlit.app/

Or run locally:

```bash
streamlit run src/shopee_transfer/web/app.py
```

The web app provides:
1. Market selection and exchange rate configuration
2. Drag-and-drop file upload with auto-detection
3. Product preview and price conversion table (with CSV export)
4. One-click transform and download
5. Step-by-step upload guide for the target market

## What Gets Transferred

| Data | Source Export | Handling |
|---|---|---|
| Product Name & Description | basic_info | Direct copy |
| Price & Stock | sales_info | Price converted using exchange rate |
| Weight & Dimensions | shipping_info | Direct copy |
| Images (cover + 8) | media_info | URL passthrough (shared CDN) |
| Category | media_info / dts_info | Mapped via config file |
| Variations (color, size) | sales_info + media_info | Restructured to upload format |
| Days to Ship | dts_info | Direct copy |
| Purchase Qty Limits | sales_info | Direct copy |
| Shipping Channels | shipping_info | **Not mapped** (differs per market, defaults to "On") |

## Project Structure

```
ShopeeSC/
  pyproject.toml                  # Project config and dependencies
  index.html                      # Pitch deck (Vercel deployment entry point)
  listing-cross-market-transfer-pitch-v2.html  # Stakeholder pitch deck (open in browser)
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
      app.py                      # Streamlit web app (5-step wizard UI)
      styles.py                   # Shopee brand styling and UI components
  tests/                          # Unit tests covering all modules
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

## Pitch Deck

A self-contained HTML pitch deck is included at [`listing-cross-market-transfer-pitch-v2.html`](listing-cross-market-transfer-pitch-v2.html) for stakeholder presentations (also served via Vercel at the link above as `index.html`). Open it directly in any browser — no dependencies required. It covers:

- Problem statement and strategic context for cross-border sellers
- Approach evaluation (why file-based transformation was chosen over RPA, API, and manual processes)
- Delivered solution (CLI + Web App) and immediate value add
- Future evolution path with Shopee Open API integration
- Phased roadmap (Q2 2026 → 2027)

## Limitations

- Shipping channels cannot be auto-mapped between markets (different channel sets per market)
- Category mapping requires manual setup per market pair
- Upload file must be under 3MB / ~500 products (Shopee limit)
- Shopee-generated xlsx files require the `calamine` engine to read (openpyxl compatibility issue)
