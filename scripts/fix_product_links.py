import os
import sys
import django

# Add the project root to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend', 'kijeka'))
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
        # If productLink is empty or suspicious, fix it
        slug = slugify(p.productName)
        if not p.productLink or p.productLink == "":
            print(f"Updating empty link for: {p.productName} -> {slug}")
            p.productLink = slug
            p.save()
            count += 1
        elif p.productLink != slug:
            # Check if current link is significantly different
            # We don't want to break existing good links, but we want to ensure robustness
            # For now, let's just log it
            print(f"Current link: {p.productLink} | Suggested slug: {slug}")
            
    print(f"Finished. Updated {count} products.")

if __name__ == "__main__":
    fix_links()
