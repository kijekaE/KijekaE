#!/usr/bin/env python3
"""
Pure sqlite3 script to replace .png -> .webp in known file columns.
Creates a JSON backup before applying changes.

Usage:
  # Dry-run (preview only)
  python scripts/update_db_sqlite.py

  # Apply changes
  python scripts/update_db_sqlite.py --apply
"""
import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[1] / 'db.sqlite3'

TABLE_COLUMNS = [
    ('api_product', 'id', 'images'),
    ('api_productimage', 'id', 'image1'),
    ('api_productimage', 'id', 'image2'),
    ('api_productimage', 'id', 'image3'),
    ('api_productimage', 'id', 'image4'),
    ('api_productimage', 'id', 'image5'),
    ('api_productimage', 'id', 'image6'),
    ('api_productimage', 'id', 'image7'),
    ('api_clients', 'id', 'image'),
    ('api_youtubevideo', 'id', 'poster'),
    ('api_blog', 'id', 'image'),
]


def find_png_rows(conn):
    cur = conn.cursor()
    changes = []
    for table, pk_col, col in TABLE_COLUMNS:
        # check if column exists in table
        try:
            cur.execute(f"PRAGMA table_info('{table}')")
            cols = [r[1] for r in cur.fetchall()]
            if col not in cols:
                continue
        except sqlite3.OperationalError:
            continue
        # look for png, jpg, jpeg (case-insensitive)
        sql = f"SELECT {pk_col}, {col} FROM {table} WHERE lower(coalesce({col},'')) LIKE '%.png' OR lower(coalesce({col},'')) LIKE '%.jpg' OR lower(coalesce({col},'')) LIKE '%.jpeg'"
        for row in cur.execute(sql):
            pk, val = row
            if not val:
                continue
            old = val
            low = old.lower()
            if low.endswith('.png') or low.endswith('.jpg') or low.endswith('.jpeg'):
                # replace final extension with .webp
                new = old[: old.rfind('.')] + '.webp'
                changes.append({'table': table, 'pk_col': pk_col, 'pk': pk, 'col': col, 'old': old, 'new': new})
    return changes


def apply_changes(conn, changes):
    cur = conn.cursor()
    for ch in changes:
        table = ch['table']
        col = ch['col']
        pk_col = ch['pk_col']
        pk = ch['pk']
        new = ch['new']
        cur.execute(f"UPDATE {table} SET {col} = ? WHERE {pk_col} = ?", (new, pk))
    conn.commit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='Apply updates to DB')
    ap.add_argument('--backup', help='Backup file path (defaults to changes_backup_TIMESTAMP.json)')
    args = ap.parse_args()

    if not DB_PATH.exists():
        print('Database not found at', DB_PATH)
        return

    conn = sqlite3.connect(str(DB_PATH))
    changes = find_png_rows(conn)
    print(f'Found {len(changes)} items to change in DB')
    if len(changes) > 0:
        stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        backup_path = Path(args.backup) if args.backup else Path(f'changes_backup_db_{stamp}.json')
        backup_path.write_text(json.dumps(changes, indent=2, ensure_ascii=False), encoding='utf8')
        print('Wrote JSON backup to', backup_path)

    if args.apply and changes:
        apply_changes(conn, changes)
        print('Applied updates to DB')
    else:
        print('Dry-run; no changes applied. Re-run with --apply to modify DB')


if __name__ == '__main__':
    main()
