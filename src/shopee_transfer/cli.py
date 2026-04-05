"""CLI entry point for Shopee cross-market listing transfer."""

from __future__ import annotations

from pathlib import Path

import click

from .mapper import transform_products
from .models import TransformConfig
from .reader import read_and_merge_exports
from .writer import write_upload_file


@click.group()
def cli():
    """Shopee cross-market listing transfer tool.

    Transforms product listings exported from one Shopee market's Seller Center
    into the upload format for another market's Seller Center.
    """
    pass


@cli.command()
@click.option("--source", required=True, help="Source market code (e.g., my)")
@click.option("--target", required=True, help="Target market code (e.g., sg)")
@click.option("--basic-info", required=True, type=click.Path(exists=True), help="basic_info export xlsx")
@click.option("--sales-info", required=True, type=click.Path(exists=True), help="sales_info export xlsx")
@click.option("--shipping-info", required=True, type=click.Path(exists=True), help="shipping_info export xlsx")
@click.option("--dts-info", required=True, type=click.Path(exists=True), help="dts_info export xlsx")
@click.option("--media-info", required=True, type=click.Path(exists=True), help="media_info export xlsx")
@click.option("--template", required=True, type=click.Path(exists=True), help="Target market upload template xlsx")
@click.option("--exchange-rate", type=float, default=None, help="Currency exchange rate (source->target). If omitted, uses built-in static rates.")
@click.option("--output", required=True, type=click.Path(), help="Output xlsx file path")
@click.option("--config-dir", type=click.Path(exists=True), default=None, help="Config directory (default: auto-detect)")
def convert(
    source, target, basic_info, sales_info, shipping_info, dts_info, media_info,
    template, exchange_rate, output, config_dir,
):
    """Convert exported listings from source market to target market upload format."""
    config_path = Path(config_dir) if config_dir else None

    click.echo(f"Reading 5 export files from {source.upper()} Seller Center...")
    export_files = [basic_info, sales_info, shipping_info, dts_info, media_info]
    products = read_and_merge_exports(export_files)
    click.echo(f"  Parsed {len(products)} products")

    variation_count = sum(1 for p in products if p.has_variations)
    click.echo(f"  {variation_count} products have variations")

    click.echo(f"\nTransforming for {target.upper()} market...")
    transform_config = TransformConfig(
        source_market=source,
        target_market=target,
        exchange_rate=exchange_rate,
    )
    rows = transform_products(products, transform_config, config_dir=config_path)
    click.echo(f"  Generated {len(rows)} upload rows")

    click.echo(f"\nWriting upload file: {output}")
    output_path = write_upload_file(rows, template, output)
    click.echo(f"  Done! Upload file saved to: {output_path}")
    click.echo(f"\nNext steps:")
    click.echo(f"  1. Open {output_path} and review the data")
    click.echo(f"  2. Fill in any missing category IDs for the target market")
    click.echo(f"  3. Upload to {target.upper()} Seller Center: Mass Upload > Upload File")


if __name__ == "__main__":
    cli()
