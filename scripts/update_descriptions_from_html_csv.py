#!/usr/bin/env python3
"""
Update description field of all matched products in the database with the HTML from the CSV.

Usage:
  # Preview mode (dry-run):
  python scripts/update_descriptions_from_html_csv.py

  # Apply updates to database:
  python scripts/update_descriptions_from_html_csv.py --apply
"""
import argparse
import csv
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Setup Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kijeka.settings")

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import django
django.setup()

from django.db import transaction
from api.models import Product

CSV_PATH = PROJECT_ROOT / "data" / "Kijeka - product catalog HTML v2 - Products_With_HTML_v2.csv"
LOG_PATH = PROJECT_ROOT / "scripts" / "update_descriptions_from_html_csv.log"

# Setup logging
logger = logging.getLogger('description_updater')
logger.setLevel(logging.DEBUG)

# File Handler (logs details)
fh = logging.FileHandler(LOG_PATH, encoding='utf-8')
fh.setLevel(logging.DEBUG)

# Console Handler (prints progress)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

def normalize(name):
    if name is None:
        return ''
    return name.strip().lower()

def main():
    parser = argparse.ArgumentParser(description="Update Product Descriptions with HTML from CSV")
    parser.add_argument('--apply', action='store_true', help='Apply updates to the database')
    args = parser.parse_args()

    logger.info("Starting Product Description HTML Update script")
    logger.info("CSV Path: %s", CSV_PATH)
    logger.info("Log Path: %s", LOG_PATH)
    logger.info("Mode: %s", "APPLY (Database will be updated)" if args.apply else "DRY-RUN (Preview mode only)")

    # Read CSV
    if not CSV_PATH.exists():
        logger.error("CSV file not found at %s", CSV_PATH)
        sys.exit(1)

    csv_rows = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        logger.info("CSV Headers: %s", headers)
        
        # Verify headers
        if not headers or 'Product Name' not in headers or 'HTML' not in headers:
            logger.error("Required headers 'Product Name' and 'HTML' not found in CSV.")
            sys.exit(1)

        for row in reader:
            csv_rows.append(row)

    logger.info("Loaded %d rows from CSV file", len(csv_rows))

    # Fetch DB Products
    db_products = list(Product.objects.all())
    logger.info("Fetched %d products from DB", len(db_products))

    # Map DB products by normalized name
    db_map = {}
    for p in db_products:
        norm_name = normalize(p.productName)
        if norm_name:
            db_map.setdefault(norm_name, []).append(p)

    # Process and Match
    matched_records = []  # List of tuples: (Product, new_html_desc, csv_row_info)
    skipped_csv_rows = []
    
    csv_names_processed = set()

    for idx, row in enumerate(csv_rows, start=1):
        raw_name = row.get('Product Name', '')
        html_content = row.get('HTML', '')
        norm_name = normalize(raw_name)

        if not norm_name:
            logger.warning("Row %d: Empty product name - skipping", idx)
            skipped_csv_rows.append((idx, "Empty product name", raw_name))
            continue

        csv_names_processed.add(norm_name)

        matching_db_products = db_map.get(norm_name, [])
        if not matching_db_products:
            logger.warning("Row %d: Product '%s' not found in DB - skipping", idx, raw_name)
            skipped_csv_rows.append((idx, "Product not found in DB", raw_name))
            continue

        for p in matching_db_products:
            matched_records.append((p, html_content, raw_name))

    # Find DB products not found in CSV
    db_not_in_csv = []
    for p in db_products:
        norm_name = normalize(p.productName)
        if norm_name not in csv_names_processed:
            db_not_in_csv.append(p)

    # Log statistics preview
    total_to_update = len(matched_records)
    total_skipped_csv = len(skipped_csv_rows)
    total_not_in_csv = len(db_not_in_csv)

    print("\n" + "="*50)
    print("                PREVIEW REPORT")
    print("="*50)
    print(f"Total products in DB:                      {len(db_products)}")
    print(f"Total rows in CSV:                         {len(csv_rows)}")
    print(f"Matched & planned to update:               {total_to_update}")
    print(f"CSV rows not matching any DB product:      {total_skipped_csv}")
    print(f"DB products not matching any CSV row:      {total_not_in_csv}")
    print("="*50)

    if total_skipped_csv > 0:
        logger.info("CSV rows skipped (sample/list):")
        for idx, reason, name in skipped_csv_rows:
            logger.info(" - Row %d: %s (Name: '%s')", idx, reason, name)

    if total_not_in_csv > 0:
        logger.info("DB products not found in CSV (skipped from update):")
        for p in db_not_in_csv:
            logger.info(" - ID: %d, Name: '%s'", p.id, p.productName)

    print("\nPreview of first 5 matching updates:")
    for i, (p, html, raw_name) in enumerate(matched_records[:5]):
        truncated_html = (html[:100] + "...") if len(html) > 100 else html
        print(f" {i+1}. DB Product ID {p.id} ({p.productName!r}) -> CSV Name {raw_name!r}")
        print(f"    New HTML Preview: {truncated_html!r}")

    if not args.apply:
        print("\n[DRY-RUN] Script completed. Re-run with --apply to commit these updates to the database.")
        sys.exit(0)

    # Perform updates
    logger.info("Applying updates to database in a transaction...")
    updated_count = 0
    error_count = 0

    try:
        with transaction.atomic():
            for p, html, raw_name in matched_records:
                try:
                    p.description = html
                    p.save(update_fields=['description'])
                    updated_count += 1
                    logger.debug("Successfully updated Product ID %d (%s)", p.id, p.productName)
                except Exception as e:
                    error_count += 1
                    logger.error("Error updating Product ID %d (%s): %s", p.id, p.productName, e)
                    raise  # triggers transaction rollback
    except Exception as e:
        logger.exception("Transaction rolled back due to error during updates: %s", e)
        sys.exit(1)

    logger.info("--- Execution Summary ---")
    logger.info("Total CSV products processed: %d", len(csv_rows))
    logger.info("Successfully updated products: %d", updated_count)
    logger.info("Products not found in CSV (skipped DB products): %d", total_not_in_csv)
    logger.info("Update errors encountered: %d", error_count)

    print(f"\nUpdate completed successfully! {updated_count} products updated.")

if __name__ == '__main__':
    main()
