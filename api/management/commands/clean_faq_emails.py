from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.html import strip_tags
import re
import logging

from api.models import Product


class Command(BaseCommand):
    help = "Remove contact mailto lines from product HTML FAQs and replace with an answer derived from the product description."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Do not save changes; only report')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of products to process (0 = no limit)')

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        limit = options.get('limit') or None
        logger = logging.getLogger('django')

        # pattern to find the contact phrase inside an FAQ answer paragraph starting with 'A:'
        # allow for newlines or broken words inside the paragraph by using DOTALL
        contact_paragraph_pattern = re.compile(
            r"<p[^>]*>\s*(?:&bull;|A:)?\s*For.*?Detail.*?email\s*us\s*on:.*?</p>",
            flags=re.IGNORECASE | re.DOTALL,
        )

        qs = Product.objects.filter(description__icontains='info@kijeka.com')
        if limit:
            qs = qs[:limit]

        total = qs.count()
        updated = 0
        skipped = 0
        changes = []

        for prod in qs:
            orig = prod.description or ''

            # find the specific FAQ answer paragraph starting with 'A:' that contains the contact line
            if not contact_paragraph_pattern.search(orig):
                skipped += 1
                continue

            # derive answer from full description text: strip tags and take the first 1-2 sentences
            text = strip_tags(orig)
            # remove excessive whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            # get first two sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)
            summary = ''
            if sentences:
                summary = ' '.join(sentences[:2]).strip()
            if not summary:
                summary = 'Please refer to the product description above for more details.'

            replacement = f'<p>{summary}</p>'

            # replace only the first matching contact paragraph
            new_html = contact_paragraph_pattern.sub(replacement, orig, count=1)

            if new_html != orig:
                changes.append((prod.id, prod.productName))
                if not dry_run:
                    try:
                        with transaction.atomic():
                            prod.description = new_html
                            prod.save()
                            updated += 1
                    except Exception as e:
                        logger.exception('Failed to update product %s (%s): %s', prod.id, prod.productName, e)
                        skipped += 1
                else:
                    updated += 1

        self.stdout.write('\n---- Clean FAQ Email Summary ----')
        self.stdout.write(f'Total products matched: {total}')
        self.stdout.write(f'Total products updated: {updated}')
        self.stdout.write(f'Total products skipped: {skipped}')
        if changes:
            self.stdout.write('Updated product list (id, name):')
            for pid, name in changes:
                self.stdout.write(f' - {pid}: {name}')
        self.stdout.write('---------------------------------\n')
