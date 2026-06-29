import os
import sys
import django

# Add the project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kijeka.settings')
django.setup()

from api.models import Product

def slugify(text):
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text).strip('-')
    return text

def fix_links():
    products = Product.objects.all()
    count = 0
    for p in products:
        slug = slugify(p.productName)
        if not p.productLink or p.productLink == "":
            print(f"Updating empty link for: {p.productName} -> {slug}")
            p.productLink = slug
            p.save()
            count += 1
        elif p.productLink != slug or '(' in p.productLink or ')' in p.productLink:
            print(f"Updating incorrect link for: {p.productName} | {p.productLink} -> {slug}")
            p.productLink = slug
            p.save()
            count += 1
            
    print(f"Finished. Updated {count} products.")

if __name__ == "__main__":
    fix_links()
