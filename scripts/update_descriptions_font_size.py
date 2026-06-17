#!/usr/bin/env python3
"""
Update font sizes in product descriptions in the SQLite database.
- Headers (h1-h6) style font-size set to 18px.
- Paragraphs (p) style font-size set to 14px.
- Table headers (th, elements inside thead) set to 16px (along with children).
- Table body cells (td not inside thead) set to 14px (along with children).

Usage:
  # Dry run (preview changes)
  python scripts/update_descriptions_font_size.py
  
  # Apply changes
  python scripts/update_descriptions_font_size.py --apply
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from bs4 import BeautifulSoup

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

DB_PATH = PROJECT_ROOT / "db.sqlite3"
BACKUP_PATH = PROJECT_ROOT / "db.sqlite3.font_backup"

def update_style_font_size(style_str, size_val):
    if not style_str:
        return f"font-size: {size_val};"
    
    parts = [p.strip() for p in style_str.split(';') if p.strip()]
    new_parts = []
    found = False
    for part in parts:
        if ':' in part:
            k, v = part.split(':', 1)
            k_clean = k.strip().lower()
            if k_clean == 'font-size':
                new_parts.append(f"font-size: {size_val}")
                found = True
            else:
                new_parts.append(f"{k.strip()}: {v.strip()}")
        else:
            new_parts.append(part)
    if not found:
        new_parts.append(f"font-size: {size_val}")
    
    return "; ".join(new_parts) + ";"

def update_html_description(html_content):
    if not html_content:
        return html_content
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 1. Process headers (h1 to h6)
    for header_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        for tag in soup.find_all(header_tag):
            style = tag.get('style', '')
            tag['style'] = update_style_font_size(style, '18px')
            
    # 2. Process paragraphs (p)
    for tag in soup.find_all('p'):
        # Check if the paragraph is inside a table cell (if so, it is handled by the table styling logic)
        if tag.find_parent(['td', 'th']):
            continue
        style = tag.get('style', '')
        tag['style'] = update_style_font_size(style, '14px')
        
    # 3. Process tables
    for table in soup.find_all('table'):
        # 3a. Update <thead> elements to 16px
        thead = table.find('thead')
        if thead:
            for el in thead.find_all(True):
                style = el.get('style', '')
                el['style'] = update_style_font_size(style, '16px')
        
        # 3b. Update <th> elements and their children (that aren't cells/tables/headers) to 16px
        for th in table.find_all('th'):
            style = th.get('style', '')
            th['style'] = update_style_font_size(style, '16px')
            for child in th.find_all(True):
                if child.name not in ['table', 'thead', 'tbody', 'tr', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    child_style = child.get('style', '')
                    child['style'] = update_style_font_size(child_style, '16px')
                    
        # 3c. Update <td> elements (not inside thead) and their children to 14px
        for td in table.find_all('td'):
            parent_thead = td.find_parent('thead')
            if not parent_thead:
                style = td.get('style', '')
                td['style'] = update_style_font_size(style, '14px')
                for child in td.find_all(True):
                    if child.name not in ['table', 'thead', 'tbody', 'tr', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        child_style = child.get('style', '')
                        child['style'] = update_style_font_size(child_style, '14px')
        
    return str(soup)

def main():
    parser = argparse.ArgumentParser(description="Update Product Descriptions font sizes (including tables) in DB")
    parser.add_argument('--apply', action='store_true', help='Commit changes to the database')
    args = parser.parse_args()

    print("=" * 60)
    print("      PRODUCT DESCRIPTION FONT SIZE UPDATER (WITH TABLES)")
    print("=" * 60)
    print("Mode:", "APPLY (Writing changes to DB)" if args.apply else "DRY-RUN (Preview mode only)")
    print("Project Root:", PROJECT_ROOT)
    print("Database Path:", DB_PATH)
    print("-" * 60)

    # 1. Check database exists
    if not DB_PATH.exists():
        print(f"Error: Database file not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    # 2. Query products
    products = Product.objects.all()
    print(f"Found {products.count()} products in the database.")

    # 3. Create backup if applying and backup doesn't exist yet
    if args.apply:
        if not BACKUP_PATH.exists():
            print(f"Creating database backup at {BACKUP_PATH}...")
            shutil.copy2(DB_PATH, BACKUP_PATH)
            print("Backup created successfully.")
        else:
            print(f"Backup already exists at {BACKUP_PATH}. Skipping backup creation.")

    # 4. Process updates
    to_update = []
    for p in products:
        if not p.description:
            continue
        original_desc = p.description
        updated_desc = update_html_description(original_desc)
        if original_desc != updated_desc:
            to_update.append((p, original_desc, updated_desc))

    print(f"Identified {len(to_update)} products needing updates.")
    print("-" * 60)

    if not to_update:
        print("All product descriptions are already up to date. No changes needed.")
        sys.exit(0)

    # Preview first 3 updates
    print("Preview of first 3 updates:")
    for idx, (p, orig, new) in enumerate(to_update[:3], 1):
        print(f"\n{idx}. Product ID: {p.id} | Name: {p.productName}")
        print("Original description length:", len(orig))
        print("Updated description length:", len(new))
        
        # Check if table exists in original/new to show a table preview
        if 'table' in new.lower():
            table_idx = new.lower().find('<table')
            snippet_new = new[table_idx:table_idx+500]
            print("Updated Table (snippet):", snippet_new.replace('\n', ' '))
        else:
            print("Original (snippet):", orig[:200].replace('\n', ' '))
            print("Updated (snippet):", new[:200].replace('\n', ' '))

    if not args.apply:
        print("\n[DRY-RUN] Script completed. Re-run with --apply to commit these updates to the database.")
        sys.exit(0)

    # 5. Apply updates in a transaction
    print("\nApplying updates to the database...")
    updated_count = 0
    try:
        with transaction.atomic():
            for p, _, new_desc in to_update:
                p.description = new_desc
                p.save(update_fields=['description'])
                updated_count += 1
    except Exception as e:
        print(f"Error occurred: {e}. Transaction rolled back.", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully updated {updated_count} product descriptions in the database.")
    print("=" * 60)

if __name__ == '__main__':
    main()
