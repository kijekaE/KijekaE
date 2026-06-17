from django.core.management.base import BaseCommand
from django.db import transaction
import csv
import logging
import os

from api.models import Product
import difflib


class Command(BaseCommand):
    help = "Update Product.description using HTML from a CSV file, starting after a given product name."

    def add_arguments(self, parser):
        parser.add_argument('csv_path', help='Path to the CSV file')
        parser.add_argument('--start-product', dest='start_product', default='Polypropylene Chemical Pump',
                            help='Product name to start after (exact match, case-insensitive)')
        parser.add_argument('--batch-size', dest='batch_size', type=int, default=100,
                            help='Number of updates to run per transaction batch')
        parser.add_argument('--encoding', dest='encoding', default='utf-8', help='CSV file encoding')
        parser.add_argument('--suggest-only', dest='suggest_only', action='store_true',
                    help='Do not update DB; only suggest fuzzy matches for non-matching CSV product names')
        parser.add_argument('--suggestions', dest='suggestions', type=int, default=5,
                    help='Number of fuzzy suggestions to show per unmatched name')
        parser.add_argument('--cutoff', dest='cutoff', type=float, default=0.6,
                    help='Similarity cutoff (0-1) for suggestions')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        start_product = options['start_product']
        batch_size = options['batch_size']
        encoding = options['encoding']

        logger = logging.getLogger('django')

        if not os.path.exists(csv_path):
            self.stderr.write(f'CSV file not found: {csv_path}')
            return

        try:
            with open(csv_path, 'r', encoding=encoding, newline='') as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)
        except Exception as e:
            self.stderr.write(f'Failed to read CSV: {e}')
            return

        if not rows:
            self.stdout.write('No rows found in CSV.')
            return

        # detect product name column and HTML column
        fieldnames = [fn for fn in (reader.fieldnames or [])]

        # heuristics for columns
        prod_col = None
        html_col = None
        for fn in fieldnames:
            low = fn.strip().lower()
            if low in ('product name', 'productname', 'product_name', 'name') and not prod_col:
                prod_col = fn
            if low == 'html' and not html_col:
                html_col = fn

        if not prod_col:
            # fall back to first column
            prod_col = fieldnames[0]

        if not html_col:
            # fall back to last column
            html_col = fieldnames[-1]

        # find index of the start product (exact match, case-insensitive, trimmed)
        start_index = None
        for i, row in enumerate(rows):
            name = (row.get(prod_col) or '')
            if name.strip().lower() == start_product.strip().lower():
                start_index = i
                break

        if start_index is None:
            self.stderr.write(f'Start product not found in CSV: "{start_product}"')
            return

        target_rows = rows[start_index + 1 :]
        total_csv = len(target_rows)

        updated = 0
        skipped = 0
        skipped_names = []
        errors = []

        def chunked(iterable, size):
            for i in range(0, len(iterable), size):
                yield iterable[i : i + size]

        suggest_only = options.get('suggest_only')
        suggestions_count = options.get('suggestions')
        cutoff = options.get('cutoff')

        # cache all product names for fuzzy matching
        all_product_names = list(Product.objects.values_list('productName', flat=True))

        # process in batches; each batch wrapped in a transaction
        batch_no = 0
        for batch in chunked(target_rows, batch_size or len(target_rows)):
            batch_no += 1
            try:
                if suggest_only:
                    # only compute suggestions; don't modify DB
                    for row in batch:
                        prod_name = (row.get(prod_col) or '').strip()
                        if not prod_name:
                            skipped += 1
                            skipped_names.append('(empty product name)')
                            continue

                        prod = Product.objects.filter(productName__iexact=prod_name).first()
                        if prod:
                            # exists exactly
                            continue

                        # compute close matches
                        matches = difflib.get_close_matches(prod_name, all_product_names, n=suggestions_count, cutoff=cutoff)
                        skipped += 1
                        skipped_names.append(prod_name)
                        if matches:
                            self.stdout.write(f'CSV name: "{prod_name}"\n  Suggestions:')
                            for m in matches:
                                self.stdout.write(f'   - {m}')
                        else:
                            self.stdout.write(f'CSV name: "{prod_name}"\n  Suggestions: (none)')
                else:
                    with transaction.atomic():
                        for row in batch:
                            prod_name = (row.get(prod_col) or '').strip()
                            html_content = row.get(html_col) or ''

                            if not prod_name:
                                skipped += 1
                                skipped_names.append('(empty product name)')
                                continue

                            try:
                                prod = Product.objects.filter(productName__iexact=prod_name).first()
                                if not prod:
                                    skipped += 1
                                    skipped_names.append(prod_name)
                                    logger.warning('Product not found: %s', prod_name)
                                    continue

                                # assign HTML exactly as provided
                                prod.description = html_content
                                prod.save()
                                updated += 1
                            except Exception as e:
                                errors.append((prod_name, str(e)))
                                logger.exception('Error updating product %s', prod_name)
                                # re-raise to rollback this batch and stop further processing
                                raise
            except Exception as e:
                self.stderr.write(f'Batch {batch_no} failed and was rolled back: {e}')
                self.stderr.write('Aborting further processing.')
                break

        # print summary
        self.stdout.write('\n---- Update Summary ----')
        self.stdout.write(f'Total CSV products processed: {total_csv}')
        self.stdout.write(f'Total products updated: {updated}')
        self.stdout.write(f'Total products skipped (not found or empty name): {skipped}')
        if skipped_names:
            self.stdout.write('Skipped product names:')
            for name in skipped_names:
                self.stdout.write(f' - {name}')

        if errors:
            self.stdout.write('\nErrors encountered:')
            for name, msg in errors:
                self.stdout.write(f' - {name}: {msg}')

        self.stdout.write('-------------------------\n')
