#!/usr/bin/env python3
import csv
import sqlite3
import shutil
import os
import sys
import logging
from datetime import datetime

DB_PATH = '/Users/vrushank/Documents/Work/Pruthatek/Projects/KijekaE/db.sqlite3'
CSV_PATH = '/Users/vrushank/Documents/Work/Pruthatek/Projects/KijekaE/data/Products_With_Catalogue_Content_HTML.csv'
BACKUP_PATH = DB_PATH + '.bak'
LOG_PATH = '/Users/vrushank/Documents/Work/Pruthatek/Projects/KijekaE/scripts/update_products_from_csv_after_ppp.log'
TARGET = 'Polypropylene Chemical Pump'
BATCH_SIZE = 100

# Setup logging
logger = logging.getLogger('csv_db_updater')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOG_PATH)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(fmt)
ch.setFormatter(fmt)
logger.addHandler(fh)
logger.addHandler(ch)

def backup_db():
    if not os.path.exists(DB_PATH):
        logger.error('DB not found at %s', DB_PATH)
        sys.exit(1)
    if not os.path.exists(BACKUP_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
        logger.info('Backup created at %s', BACKUP_PATH)
    else:
        logger.info('Backup already exists at %s', BACKUP_PATH)

def read_csv_after_target(csv_path, target_name):
    rows = []
    started = False
    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            logger.error('CSV is empty')
            return rows
        for row in reader:
            if not started:
                if len(row) > 0 and row[0].strip() == target_name:
                    started = True
                    continue
                else:
                    continue
            rows.append(row)
    return rows


def normalize(name):
    if name is None:
        return ''
    return name.strip()


def main():
    logger.info('Starting CSV -> DB update. Target skip row: %s', TARGET)
    backup_db()

    rows = read_csv_after_target(CSV_PATH, TARGET)
    total_rows = len(rows)
    logger.info('Total CSV rows to process (after target): %d', total_rows)

    if total_rows == 0:
        logger.info('Nothing to process. Exiting.')
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = None
    cur = conn.cursor()

    processed = 0
    updated = 0
    skipped = 0
    skipped_names = []
    batch_updates = 0

    try:
        conn.execute('BEGIN')
        for idx, row in enumerate(rows, start=1):
            try:
                product_name = normalize(row[0]) if len(row) > 0 else ''
                html = row[9] if len(row) > 9 else ''

                if product_name == '':
                    logger.warning('Row %d: empty product name — skipping', idx)
                    skipped += 1
                    skipped_names.append('(empty name at row %d)' % idx)
                    continue

                # Case-insensitive trimmed match
                cur.execute('SELECT id FROM api_product WHERE lower(trim(productName)) = lower(trim(?))', (product_name,))
                ids = [r[0] for r in cur.fetchall()]

                if not ids:
                    logger.info('Row %d: "%s" not found in DB — skipping', idx, product_name)
                    skipped += 1
                    skipped_names.append(product_name)
                else:
                    for _id in ids:
                        cur.execute('UPDATE api_product SET description = ? WHERE id = ?', (html, _id))
                        updated += 1
                        batch_updates += 1
                    logger.info('Row %d: "%s" updated for %d DB row(s)', idx, product_name, len(ids))

                processed += 1

                # Batch commit
                if batch_updates >= BATCH_SIZE:
                    conn.commit()
                    logger.info('Committed batch of %d updates', batch_updates)
                    batch_updates = 0
                    conn.execute('BEGIN')

            except Exception as e:
                logger.exception('Error processing CSV row %d: %s', idx, e)
                raise

        # Final commit
        conn.commit()
        logger.info('Final commit done')

    except Exception as e:
        conn.rollback()
        logger.exception('Exception occurred — rolled back. %s', e)
        logger.info('See log at %s for details', LOG_PATH)
        conn.close()
        sys.exit(1)

    conn.close()

    # Summary
    logger.info('--- Summary ---')
    logger.info('Total CSV products processed: %d', processed)
    logger.info('Total products updated: %d', updated)
    logger.info('Total products skipped (not found or empty): %d', skipped)
    if skipped_names:
        logger.info('List of skipped product names:')
        for name in skipped_names:
            logger.info(' - %s', name)

    # Also write a short summary file
    summary_path = os.path.join(os.path.dirname(LOG_PATH), 'update_summary_%s.txt' % datetime.now().strftime('%Y%m%d_%H%M%S'))
    with open(summary_path, 'w', encoding='utf-8') as sf:
        sf.write('Total CSV products processed: %d\n' % processed)
        sf.write('Total products updated: %d\n' % updated)
        sf.write('Total products skipped: %d\n' % skipped)
        sf.write('Skipped product names:\n')
        for name in skipped_names:
            sf.write('- %s\n' % name)

    logger.info('Summary written to %s', summary_path)

if __name__ == '__main__':
    main()
