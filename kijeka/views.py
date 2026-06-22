from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from api.models import Blog, Category, SubCategory, Product
from django.http import FileResponse
from django.db.models import F
from django.shortcuts import get_object_or_404
import os
import re
import json
import time
import threading
from django.conf import settings
from django.utils.html import strip_tags
try:
    import requests as http_requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Local SEO: IP-based city geolocation with in-process TTL cache
# ---------------------------------------------------------------------------
_ip_cache = {}          # { ip_str: (city_str, timestamp) }
_ip_cache_lock = threading.Lock()
_IP_CACHE_TTL = 86400   # 24 hours

# Known bot/crawler User-Agent substrings – return generic location for these
_BOT_UA_PATTERNS = [
    "googlebot", "bingbot", "slurp", "duckduckbot", "baiduspider",
    "yandexbot", "facebot", "ia_archiver", "semrushbot", "ahrefsbot",
    "mj12bot", "dotbot", "rogerbot", "exabot", "sogou",
]

# ---------------------------------------------------------------------------
# City locations: slug → display name (used for static SEO landing pages)
# ---------------------------------------------------------------------------
CITY_LOCATIONS = {
    "ahmedabad":   "Ahmedabad",
    "surat":       "Surat",
    "vadodara":    "Vadodara",
    "bhavnagar":   "Bhavnagar",
    "kutch":       "Kutch",
    "himmatnagar": "Himmatnagar",
    "vatva":       "Vatva",
    "kathwada":    "Kathwada",
    "kalol":       "Kalol",
    "gandhidham":  "Gandhidham",
    "mehsana":     "Mehsana",
    "chhatral":    "Chhatral",
    "pune":        "Pune",
    "bangalore":   "Bangalore",
    "mangalore":   "Mangalore",
    "mumbai":      "Mumbai",
    "hyderabad":   "Hyderabad",
    "chennai":     "Chennai",
    "noida":       "Noida",
    "bhopal":      "Bhopal",
    "faridabad":   "Faridabad",
    "indore":      "Indore",
    "rohtak":      "Rohtak",
    "ambala":      "Ambala",
    "gurugram":    "Gurugram",
    "jaipur":      "Jaipur",
    "udaipur":     "Udaipur",
    "delhi":       "Delhi",
    "gujarat":     "Gujarat",
    "maharashtra": "Maharashtra",
    "rajasthan":   "Rajasthan",
    "pan-india":   "Pan India",
}


def _is_bot(request):
    ua = (request.META.get("HTTP_USER_AGENT") or "").lower()
    return any(pat in ua for pat in _BOT_UA_PATTERNS)


def get_client_ip(request):
    """Extract real client IP, respecting X-Forwarded-For."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # Take the first (leftmost) address – the original client
        ip = xff.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "")
    # Ignore loopback / private addresses
    if not ip or ip in ("127.0.0.1", "::1") or ip.startswith("192.168.") or ip.startswith("10."):
        return None
    return ip


def get_city_from_ip(request):
    """
    Return the city name for the request's IP address.
    Falls back to "India" for bots, unknown IPs, or on any error.
    Results are cached for 24 hours in-process.
    """
    if _is_bot(request) or not _REQUESTS_AVAILABLE:
        return "India"

    ip = get_client_ip(request)
    if not ip:
        return "India"

    now = time.time()
    with _ip_cache_lock:
        if ip in _ip_cache:
            city, ts = _ip_cache[ip]
            if now - ts < _IP_CACHE_TTL:
                return city

    try:
        resp = http_requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,city,country",
            timeout=1.5,
        )
        data = resp.json()
        if data.get("status") == "success" and data.get("city"):
            city = data["city"]
        else:
            city = "India"
    except Exception:
        city = "India"

    with _ip_cache_lock:
        _ip_cache[ip] = (city, now)

    return city


# ---------------------------------------------------------------------------
# City SEO helpers
# ---------------------------------------------------------------------------

def _build_city_links_block(slug, product_name, current_city_slug, page_type="product"):
    """
    Build a hidden <noscript> block linking to all city variants of this page.
    Invisible to users but crawlable by Googlebot — ensures Google discovers
    every city landing page from the main product/category page.
    """
    links = []
    for city_slug, city_name in CITY_LOCATIONS.items():
        if city_slug == current_city_slug:
            continue
        if page_type == "product":
            url = f"/product/{slug}/{city_slug}/"
        else:
            url = f"/{slug}/{city_slug}/"
        links.append(f'<a href="{url}">{product_name} in {city_name}</a>')
    links_str = "\n".join(links)
    return (
        f'<noscript><div id="kijeka-local-seo-links" style="display:none">'
        f'<h3>{product_name} Available Across India</h3>'
        f'{links_str}</div></noscript>'
    )


def city_product_view(request, link, city_slug):
    """
    Dedicated city-specific product landing page.
    URL: /product/<product-slug>/<city-slug>/
    Google indexes these with a static city-baked title, enabling local search results.
    """
    city_slug = city_slug.rstrip("/").lower()

    if city_slug not in CITY_LOCATIONS:
        return page_not_found_view(request)

    city_name = CITY_LOCATIONS[city_slug]
    link_param = link.rstrip("/")

    # Product lookup (same logic as product_detail_view)
    product = Product.objects.filter(productLink=link_param).first()
    if not product:
        product = Product.objects.filter(productName=link_param).first()
    if not product:
        normalized_param = link_param.lower().replace(" ", "-")
        product = Product.objects.filter(productLink=normalized_param).first()
        if not product:
            for p in Product.objects.all():
                if p.productName.lower().replace(" ", "-") == normalized_param:
                    product = p
                    break

    if not product:
        return page_not_found_view(request)

    product_name = product.productName
    # Dynamic city title — Google will index this exactly as shown
    title = f"{product_name} Manufacturers and Suppliers {city_name}, India"
    base_desc = product.metaDescription or product.description or ""
    base_desc = strip_tags(base_desc).strip()
    if base_desc and len(base_desc) > 20:
        loc_prefix = f"Find {product_name} Manufacturers and Suppliers in {city_name}, India. "
        combined = loc_prefix + base_desc
        description = combined[:152] + "..." if len(combined) > 155 else combined
    else:
        description = (
            f"Find {product_name} Manufacturers and Suppliers in {city_name}, India. "
            "Kijeka Engineers is India's trusted manufacturer of premium material handling equipment since 1980."
        )
    og_image = product.images.url if product.images else None
    product_schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product_name,
        "description": description,
        "brand": {"@type": "Brand", "name": "Kijeka Engineers"},
        "manufacturer": {
            "@type": "Organization",
            "name": "Kijeka Engineers Pvt. Ltd.",
            "url": "https://www.kijeka.com",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Ahmedabad",
                "addressRegion": "Gujarat",
                "addressCountry": "IN"
            }
        },
        "offers": {
            "@type": "Offer",
            "url": f"https://www.kijeka.com/product/{link_param}/{city_slug}/",
            "priceCurrency": "INR",
            "availability": "https://schema.org/InStock",
            "areaServed": city_name,
            "seller": {"@type": "Organization", "name": "Kijeka Engineers Pvt. Ltd."}
        }
    }
    if og_image:
        product_schema["image"] = (
            "https://www.kijeka.com" + og_image if og_image.startswith("/") else og_image
        )

    canonical = f"https://www.kijeka.com/product/{link_param}/{city_slug}/"
    raw_html = load_template_file("index.html")
    injected_html = inject_seo_meta(
        raw_html, title, description, canonical, og_image,
        extra_schema_json=product_schema
    )
    # Inject internal city links so Google can crawl all city variants
    city_block = _build_city_links_block(link_param, product_name, city_slug, "product")
    injected_html = injected_html.replace("</body>", city_block + "\n</body>", 1)
    return HttpResponse(injected_html, content_type="text/html")


def inject_seo_meta(html_content, title, description, canonical_url=None, og_image_url=None, extra_schema_json=None):
    html_content = re.sub(r'<title>.*?</title>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<meta[^>]*name=["\']title["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<meta[^>]*name=["\']description["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<link[^>]*rel=["\']canonical["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<meta[^>]*property=["\']og:title["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<meta[^>]*property=["\']og:description["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<meta[^>]*property=["\']og:url["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<meta[^>]*property=["\']og:image["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<meta[^>]*property=["\']og:type["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<meta[^>]*name=["\']twitter:card["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<meta[^>]*name=["\']twitter:title["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<meta[^>]*name=["\']twitter:description["\'][^>]*>', '', html_content, flags=re.IGNORECASE)
    html_content = re.sub(r'<meta[^>]*name=["\']twitter:image["\'][^>]*>', '', html_content, flags=re.IGNORECASE)

    title = title.strip() if title else "Kijeka Engineers"
    if description:
        description = strip_tags(description).strip()
        description = description.replace("\n", " ").replace('"', '&quot;')
        if len(description) > 155:
            description = description[:152] + "..."
    else:
        description = "KIJEKA ENGINEERS is a leading Indian material handling equipment manufacturer and supplier of high quality material handling products and industrial machinery equipment since 1980."

    seo_tags = []
    seo_tags.append(f'<title data-rh="true">{title}</title>')
    seo_tags.append(f'<meta name="title" content="{title}" data-rh="true">')
    seo_tags.append(f'<meta name="description" content="{description}" data-rh="true">')
    seo_tags.append(f'<meta property="og:title" content="{title}" data-rh="true">')
    seo_tags.append(f'<meta property="og:description" content="{description}" data-rh="true">')
    seo_tags.append('<meta property="og:type" content="website" data-rh="true">')
    
    if canonical_url:
        seo_tags.append(f'<link rel="canonical" href="{canonical_url}" data-rh="true">')
        seo_tags.append(f'<meta property="og:url" content="{canonical_url}" data-rh="true">')
        
    if og_image_url:
        if og_image_url.startswith('/'):
            og_image_url = "https://www.kijeka.com" + og_image_url
        seo_tags.append(f'<meta property="og:image" content="{og_image_url}" data-rh="true">')
    else:
        seo_tags.append('<meta property="og:image" content="https://www.kijeka.com/static/images/KijekaLogo.webp" data-rh="true">')

    seo_tags.append('<meta name="twitter:card" content="summary_large_image" data-rh="true">')
    seo_tags.append(f'<meta name="twitter:title" content="{title}" data-rh="true">')
    seo_tags.append(f'<meta name="twitter:description" content="{description}" data-rh="true">')
    if og_image_url:
        if og_image_url.startswith('/'):
            og_image_url = "https://www.kijeka.com" + og_image_url
        seo_tags.append(f'<meta name="twitter:image" content="{og_image_url}" data-rh="true">')

    if extra_schema_json:
        seo_tags.append(f'<script type="application/ld+json">{json.dumps(extra_schema_json)}</script>')

    seo_tags_str = "\n".join(seo_tags)

    head_match = re.search(r'<head[^>]*>', html_content, flags=re.IGNORECASE)
    if head_match:
        pos = head_match.end()
        html_content = html_content[:pos] + "\n" + seo_tags_str + html_content[pos:]
    else:
        html_content = seo_tags_str + "\n" + html_content

    return html_content

def load_template_file(template_path):
    file_path = os.path.join(settings.BASE_DIR, "templates", template_path)
    if not os.path.exists(file_path):
        file_path = os.path.join(settings.BASE_DIR, "templates", "index.html")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def page_not_found_view(request):
    """Serve the React 404 page with a proper 404 HTTP status."""
    title = "404 Page Not Found | Kijeka Engineers Private Limited"
    description = (
        "Oops! Looks like the page you were looking for couldn't be found. "
        "Kijeka is a leading provider of top-quality handling equipment solutions "
        "for industries worldwide."
    )
    canonical = "https://www.kijeka.com/page-not-found/"
    raw_html = load_template_file("page-not-found/index.html")
    injected_html = inject_seo_meta(raw_html, title, description, canonical)
    return HttpResponse(injected_html, status=404, content_type="text/html")


def handler404(request, exception):
    return page_not_found_view(request)

def blogDynamic(request, link):
    link = link.rstrip("/")
    blog = Blog.objects.filter(blogLink__iexact=link).first()
    if not blog:
        title_guess = link.replace("-", " ")
        blog = Blog.objects.filter(title__iexact=title_guess).first()

    if not blog:
        return page_not_found_view(request)

    Blog.objects.filter(id=blog.id).update(views=F("views") + 1)
    title = f"{blog.title} | Kijeka Blog"
    description = blog.metaDescription or blog.description
    og_image = blog.image.url if blog.image else None

    canonical = f"https://www.kijeka.com/blog/{link}/"
    raw_html = load_template_file("index.html")
    injected_html = inject_seo_meta(raw_html, title, description, canonical, og_image)
    return HttpResponse(injected_html, content_type="text/html")


@csrf_exempt
def pdfCatalog(request):
    return redirect("/static/Kijeka_Catalogue.pdf")


@csrf_exempt
@login_required(login_url="/dashboard/login/")
def dashboard(request):
    return render(request, "admin.html")


@csrf_exempt
def loginPage(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def youtubevideos(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def review(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def addProducts(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def hotProducts(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def allProducts(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def clientLogos(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def blog(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def newBlog(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def draftsBlog(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def reviewBlog(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def approvedBlog(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def publishedBlog(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def rejectedBlog(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def deleteBlog(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def imageSlider(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def contactdetails(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def reachusform(request):
    return render(request, "admin.html")


@login_required(login_url="/dashboard/login/")
def careers(request):
    return render(request, "admin.html")


def home_view(request):
    title = "Material Handling Equipment Manufacturer | Kijeka India"
    description = "Kijeka Engineers is a leading manufacturer of Material Handling Equipment in India. We supply premium warehouse lifts, stackers and custom handling systems."
    canonical = "https://www.kijeka.com/"

    from datetime import date
    years_exp = date.today().year - 1980

    extra_schema = {
      "@context": "https://schema.org",
      "@graph": [
        # ------------------------------------------------------------------
        # 1. Organization — ties kijeka.com to ALL external profiles via sameAs
        #    This triggers Google's Knowledge Panel and entity recognition
        # ------------------------------------------------------------------
        {
          "@type": "Organization",
          "@id": "https://www.kijeka.com/#organization",
          "name": "Kijeka Engineers Pvt. Ltd.",
          "alternateName": "Kijeka Engineers",
          "url": "https://www.kijeka.com",
          "logo": {
            "@type": "ImageObject",
            "url": "https://www.kijeka.com/static/images/KijekaLogo.webp",
            "width": 200,
            "height": 60
          },
          "image": "https://www.kijeka.com/static/images/KijekaLogo.webp",
          "description": f"India's trusted manufacturer & supplier of premium material handling equipment — Stackers, Pallet Trucks, Scissor Lifts, Cranes, Drum Handling Equipment and more. {years_exp}+ years of excellence since 1980.",
          "foundingDate": "1980",
          "numberOfEmployees": {"@type": "QuantitativeValue", "minValue": 50, "maxValue": 200},
          "contactPoint": [
            {
              "@type": "ContactPoint",
              "contactType": "customer service",
              "areaServed": "IN",
              "availableLanguage": ["English", "Hindi", "Gujarati"]
            }
          ],
          # ----------------------------------------------------------------
          # sameAs — tells Google these are all the SAME business entity
          # This is the most powerful entity-linking signal available
          # ----------------------------------------------------------------
          "sameAs": [
            "https://www.indiamart.com/kijeka-engineers/",
            "https://www.tradeindia.com/kijeka-engineers-pvt-ltd-1797/",
            "https://www.exportersindia.com/kijekaengineers/",
            "https://www.facebook.com/kijekaengg/",
            "https://www.instagram.com/kijeka/",
            "https://x.com/kijeka",
            "https://in.pinterest.com/kijekaengg/",
            "https://www.youtube.com/c/kijekamhe",
            "https://www.justdial.com/Ahmedabad/Kijeka-Engineers-Pvt-Ltd-Near-Ugvcl-Office-Bol/079PXX79-XX79-180222183256-J5I9_BZDET",
            "https://www.zaubacorp.com/KIJEKA-ENGINEERS-PRIVATE-LIMITED-U29190GJ2008PTC052992",
            "https://www.zoominfo.com/c/kijeka-engineers-private-ltd/354139510",
            "https://www.ambitionbox.com/overview/kijeka-engineers-overview"
          ]
        },
        # ------------------------------------------------------------------
        # 2. LocalBusiness — full NAP + geo + area served (critical for Maps)
        # ------------------------------------------------------------------
        {
          "@type": ["LocalBusiness", "Manufacturer"],
          "@id": "https://www.kijeka.com/#localbusiness",
          "name": "Kijeka Engineers Pvt. Ltd.",
          "url": "https://www.kijeka.com",
          "logo": "https://www.kijeka.com/static/images/KijekaLogo.webp",
          "image": "https://www.kijeka.com/static/images/KijekaLogo.webp",
          "priceRange": "₹₹",
          "currenciesAccepted": "INR",
          "paymentAccepted": "Cash, Bank Transfer, Cheque",
          "address": {
            "@type": "PostalAddress",
            "streetAddress": "Plot No. 2411, Phase IV, GIDC Vatva",
            "addressLocality": "Ahmedabad",
            "addressRegion": "Gujarat",
            "postalCode": "382445",
            "addressCountry": "IN"
          },
          "geo": {
            "@type": "GeoCoordinates",
            "latitude": "22.9713",
            "longitude": "72.6421"
          },
          "areaServed": [
            "Ahmedabad", "Surat", "Vadodara", "Bhavnagar", "Kutch",
            "Himmatnagar", "Vatva", "Kathwada", "Kalol", "Gandhidham",
            "Mehsana", "Chhatral", "Pune", "Bangalore", "Mangalore",
            "Mumbai", "Hyderabad", "Chennai", "Noida", "Bhopal",
            "Faridabad", "Indore", "Rohtak", "Ambala", "Gurugram",
            "Jaipur", "Udaipur", "Gujarat", "Maharashtra", "Rajasthan",
            "India"
          ],
          "hasMap": "https://maps.google.com/?q=Kijeka+Engineers+Pvt+Ltd+Vatva+Ahmedabad",
          "openingHoursSpecification": [
            {
              "@type": "OpeningHoursSpecification",
              "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
              "opens": "09:00",
              "closes": "18:00"
            }
          ],
          "knowsAbout": [
            "Material Handling Equipment", "Stackers", "Pallet Trucks",
            "Scissor Lift", "Industrial Cranes", "Drum Handling Equipment",
            "Warehouse Equipment", "Forklift Accessories", "Ladders"
          ],
          "sameAs": [
            "https://www.indiamart.com/kijeka-engineers/",
            "https://www.tradeindia.com/kijeka-engineers-pvt-ltd-1797/",
            "https://www.exportersindia.com/kijekaengineers/",
            "https://www.facebook.com/kijekaengg/",
            "https://www.instagram.com/kijeka/",
            "https://x.com/kijeka",
            "https://in.pinterest.com/kijekaengg/",
            "https://www.youtube.com/c/kijekamhe",
            "https://www.justdial.com/Ahmedabad/Kijeka-Engineers-Pvt-Ltd-Near-Ugvcl-Office-Bol/079PXX79-XX79-180222183256-J5I9_BZDET",
            "https://www.zaubacorp.com/KIJEKA-ENGINEERS-PRIVATE-LIMITED-U29190GJ2008PTC052992",
            "https://www.zoominfo.com/c/kijeka-engineers-private-ltd/354139510",
            "https://www.ambitionbox.com/overview/kijeka-engineers-overview"
          ]
        },
        # ------------------------------------------------------------------
        # 3. SiteNavigationElement — sitelinks structure
        # ------------------------------------------------------------------
        {
          "@type": "SiteNavigationElement",
          "@id": "https://www.kijeka.com/#navigation",
          "name": "Home",
          "url": "https://www.kijeka.com/"
        },
        {
          "@type": "SiteNavigationElement",
          "name": "Stackers",
          "url": "https://www.kijeka.com/stackers/"
        },
        {
          "@type": "SiteNavigationElement",
          "name": "Pallet Trucks",
          "url": "https://www.kijeka.com/pallet-trucks/"
        },
        {
          "@type": "SiteNavigationElement",
          "name": "Hot Products",
          "url": "https://www.kijeka.com/our-products/"
        },
        {
          "@type": "SiteNavigationElement",
          "name": "Contact Us",
          "url": "https://www.kijeka.com/contact/"
        },
        {
          "@type": "SiteNavigationElement",
          "name": "Kijeka Blogs",
          "url": "https://www.kijeka.com/blog/"
        }
      ]
    }
    raw_html = load_template_file("index.html")
    injected_html = inject_seo_meta(raw_html, title, description, canonical, extra_schema_json=extra_schema)
    return HttpResponse(injected_html, content_type="text/html")


def about_view(request):
    title = "About Us | Kijeka Engineers"
    description = "Founded by Mr Rameshchandra Dave in 1980, Kijeka Engineers is a leading provider of top-tier materials handling solutions and industrial machinery equipment."
    canonical = "https://www.kijeka.com/about/"
    raw_html = load_template_file("about/index.html")
    injected_html = inject_seo_meta(raw_html, title, description, canonical)
    return HttpResponse(injected_html, content_type="text/html")

def careers_view(request):
    title = "Careers at Kijeka | Join Our Team"
    description = "Explore career opportunities at Kijeka Engineers. Join a team dedicated to innovation and excellence in material handling equipment manufacturing."
    canonical = "https://www.kijeka.com/careers/"
    raw_html = load_template_file("careers/index.html")
    injected_html = inject_seo_meta(raw_html, title, description, canonical)
    return HttpResponse(injected_html, content_type="text/html")

def blog_list_view(request):
    title = "Kijeka Blog | Industry Insights & Material Handling Guide"
    description = "Read the latest news, articles, and guides on material handling equipment, industrial automation, and safety practices from Kijeka Engineers."
    canonical = "https://www.kijeka.com/blog/"
    raw_html = load_template_file("blog/index.html")
    injected_html = inject_seo_meta(raw_html, title, description, canonical)
    return HttpResponse(injected_html, content_type="text/html")

def contact_view(request):
    title = "Contact Kijeka Engineers | Get in Touch"
    description = "Get in touch with Kijeka Engineers for customized material handling solutions, product inquiries, quotes, or on-site technical support."
    canonical = "https://www.kijeka.com/contact/"
    raw_html = load_template_file("contact/index.html")
    injected_html = inject_seo_meta(raw_html, title, description, canonical)
    return HttpResponse(injected_html, content_type="text/html")

def our_products_view(request):
    title = "Our Products | Kijeka Engineers"
    description = "Browse the extensive range of premium material handling equipment, scissor lifts, pallet trucks, cranes, drum equipments, and more by Kijeka Engineers."
    canonical = "https://www.kijeka.com/our-products/"
    raw_html = load_template_file("our-products/index.html")
    injected_html = inject_seo_meta(raw_html, title, description, canonical)
    return HttpResponse(injected_html, content_type="text/html")

def privacy_policy_view(request):
    title = "Privacy Policy | Kijeka Engineers"
    description = "Read the privacy policy of Kijeka Engineers to understand how we collect, use, and protect your personal information."
    canonical = "https://www.kijeka.com/privacy-policy/"
    raw_html = load_template_file("privacy-policy/index.html")
    injected_html = inject_seo_meta(raw_html, title, description, canonical)
    return HttpResponse(injected_html, content_type="text/html")

def terms_and_condition_view(request):
    title = "Terms & Conditions | Kijeka Engineers"
    description = "Read the terms and conditions of Kijeka Engineers governing the use of our website and purchase of our material handling products."
    canonical = "https://www.kijeka.com/terms-and-condition/"
    raw_html = load_template_file("terms-and-condition/index.html")
    injected_html = inject_seo_meta(raw_html, title, description, canonical)
    return HttpResponse(injected_html, content_type="text/html")

def product_detail_view(request, link):
    link_param = link.rstrip("/")
    product = Product.objects.filter(productLink=link_param).first()
    if not product:
        product = Product.objects.filter(productName=link_param).first()
    if not product:
        normalized_param = link_param.lower().replace(" ", "-")
        product = Product.objects.filter(productLink=normalized_param).first()
        if not product:
            for p in Product.objects.all():
                if p.productName.lower().replace(" ", "-") == normalized_param:
                    product = p
                    break

    # Detect visitor city for Local SEO
    city = get_city_from_ip(request)

    if not product:
        return page_not_found_view(request)

    product_name = product.productName
    # Build localised title
    title = f"{product_name} Manufacturers and Suppliers {city}, India"
    # Build localised description
    base_desc = product.metaDescription or product.description or ""
    base_desc = strip_tags(base_desc).strip()
    if base_desc and len(base_desc) > 20:
        loc_prefix = f"Find {product_name} Manufacturers and Suppliers in {city}, India. "
        combined = loc_prefix + base_desc
        if len(combined) > 155:
            combined = combined[:152] + "..."
        description = combined
    else:
        description = (
            f"Find {product_name} Manufacturers and Suppliers in {city}, India. "
            "Kijeka Engineers is India's trusted manufacturer of premium material handling equipment since 1980."
        )
    og_image = product.images.url if product.images else None
    # Product schema (LocalBusiness + Product)
    product_schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product_name,
        "description": description,
        "brand": {
            "@type": "Brand",
            "name": "Kijeka Engineers"
        },
        "manufacturer": {
            "@type": "Organization",
            "name": "Kijeka Engineers Pvt. Ltd.",
            "url": "https://www.kijeka.com",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Ahmedabad",
                "addressRegion": "Gujarat",
                "addressCountry": "IN"
            }
        },
        "offers": {
            "@type": "Offer",
            "url": f"https://www.kijeka.com/product/{link_param}/",
            "priceCurrency": "INR",
            "availability": "https://schema.org/InStock",
            "seller": {
                "@type": "Organization",
                "name": "Kijeka Engineers Pvt. Ltd."
            }
        }
    }
    if og_image:
        if og_image.startswith("/"):
            product_schema["image"] = "https://www.kijeka.com" + og_image
        else:
            product_schema["image"] = og_image

    canonical = f"https://www.kijeka.com/product/{link_param}/"
    raw_html = load_template_file("index.html")
    injected_html = inject_seo_meta(raw_html, title, description, canonical, og_image, extra_schema_json=product_schema)
    return HttpResponse(injected_html, content_type="text/html")

def category_view(request, link):
    link_param = link.rstrip("/").lower()

    # Detect visitor city for Local SEO
    city = get_city_from_ip(request)

    cat_obj = Category.objects.filter(categoryLink=link_param).first()
    if not cat_obj:
        title_guess = link_param.replace("-", " ")
        cat_obj = Category.objects.filter(categoryName__iexact=title_guess).first()

    if not cat_obj:
        return page_not_found_view(request)

    cat_name = cat_obj.categoryName
    title = f"{cat_name} in {city} | Kijeka Engineers"
    base_desc = cat_obj.metaDescription or cat_obj.discription or ""
    base_desc = strip_tags(base_desc).strip()
    if base_desc and len(base_desc) > 20:
        loc_prefix = f"{cat_name} in {city}. "
        combined = loc_prefix + base_desc
        if len(combined) > 155:
            combined = combined[:152] + "..."
        description = combined
    else:
        description = (
            f"Shop {cat_name} in {city} from Kijeka Engineers — "
            "India's leading material handling equipment manufacturer since 1980."
        )

    canonical = f"https://www.kijeka.com/{link_param}/"
    raw_html = load_template_file("index.html")
    injected_html = inject_seo_meta(raw_html, title, description, canonical)
    return HttpResponse(injected_html, content_type="text/html")

def subcategory_view(request, link, subLink):
    link_param = link.rstrip("/").lower()
    sublink_param = subLink.rstrip("/").lower()

    # -----------------------------------------------------------------------
    # If subLink is a known city slug, serve a city-category landing page
    # instead of a subcategory page.  This handles URLs like:
    #   /stackers/surat/  →  "Stackers in Surat | Kijeka Engineers"
    # -----------------------------------------------------------------------
    if sublink_param in CITY_LOCATIONS:
        city_name = CITY_LOCATIONS[sublink_param]
        cat_obj = Category.objects.filter(categoryLink=link_param).first()
        if not cat_obj:
            cat_obj = Category.objects.filter(
                categoryName__iexact=link_param.replace("-", " ")
            ).first()
        if not cat_obj:
            return page_not_found_view(request)
        cat_name = cat_obj.categoryName
        base_desc = cat_obj.metaDescription or cat_obj.discription or ""
        base_desc = strip_tags(base_desc).strip()
        if base_desc and len(base_desc) > 20:
            combined = f"{cat_name} in {city_name}. " + base_desc
            base_desc = combined[:152] + "..." if len(combined) > 155 else combined
        city_title = f"{cat_name} in {city_name} | Kijeka Engineers"
        city_desc = base_desc if base_desc else (
            f"Shop {cat_name} in {city_name} from Kijeka Engineers \u2014 "
            "India's leading material handling equipment manufacturer since 1980."
        )
        canonical = f"https://www.kijeka.com/{link_param}/{sublink_param}/"
        raw_html = load_template_file("index.html")
        injected_html = inject_seo_meta(raw_html, city_title, city_desc, canonical)
        # Internal city discovery links
        city_block = _build_city_links_block(link_param, cat_name, sublink_param, "category")
        injected_html = injected_html.replace("</body>", city_block + "\n</body>", 1)
        return HttpResponse(injected_html, content_type="text/html")

    # --- Normal subcategory logic below ---

    # Detect visitor city for IP-based Local SEO
    city = get_city_from_ip(request)

    subCat_obj = SubCategory.objects.filter(subCategoryLink=sublink_param).first()
    if not subCat_obj:
        title_guess = sublink_param.replace("-", " ")
        subCat_obj = SubCategory.objects.filter(subCategoryName__iexact=title_guess).first()

    if not subCat_obj:
        return page_not_found_view(request)

    sub_name = subCat_obj.subCategoryName
    category_name = subCat_obj.category.categoryName if subCat_obj.category else ""
    title = f"{sub_name} in {city} | {category_name} | Kijeka Engineers"
    base_desc = subCat_obj.discription or ""
    base_desc = strip_tags(base_desc).strip()
    if base_desc and len(base_desc) > 20:
        loc_prefix = f"{sub_name} in {city}. "
        combined = loc_prefix + base_desc
        description = combined[:152] + "..." if len(combined) > 155 else combined
    else:
        description = (
            f"Browse high-quality {sub_name} in {city} from Kijeka Engineers \u2014 "
            "India's leading material handling equipment manufacturer since 1980."
        )

    canonical = f"https://www.kijeka.com/{link_param}/{sublink_param}/"
    raw_html = load_template_file("index.html")
    injected_html = inject_seo_meta(raw_html, title, description, canonical)
    return HttpResponse(injected_html, content_type="text/html")


def generic_index_view(request, title="Kijeka Engineers | Material Handling Equipment", description=None, *args, **kwargs):
    raw_html = load_template_file("index.html")
    canonical = f"https://www.kijeka.com{request.path}"
    injected_html = inject_seo_meta(raw_html, title, description, canonical)
    return HttpResponse(injected_html, content_type="text/html")


# ---------------------------------------------------------------------------
# Dynamic sitemap — replaces the static sitemap.xml template
# Generates all URLs including product\u00d7city and category\u00d7city pages
# ---------------------------------------------------------------------------

def dynamic_sitemap_view(request):
    from django.utils.timezone import now as tz_now
    today = tz_now().strftime("%Y-%m-%d")

    # ---- Static pages ----
    static_entries = [
        ("https://www.kijeka.com/",                     "1.0", "daily"),
        ("https://www.kijeka.com/about/",               "0.8", "monthly"),
        ("https://www.kijeka.com/contact/",             "0.8", "monthly"),
        ("https://www.kijeka.com/blog/",                "0.9", "daily"),
        ("https://www.kijeka.com/our-products/",        "0.8", "weekly"),
        ("https://www.kijeka.com/careers/",             "0.6", "monthly"),
        ("https://www.kijeka.com/privacy-policy/",      "0.4", "monthly"),
        ("https://www.kijeka.com/terms-and-condition/", "0.4", "monthly"),
    ]

    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    def add_url(loc, priority, changefreq):
        clean_loc = (
            loc.replace(" ", "%20")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )
        xml_parts.append(
            f"  <url>\n"
            f"    <loc>{clean_loc}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            f"  </url>"
        )

    for loc, priority, changefreq in static_entries:
        add_url(loc, priority, changefreq)

    # ---- Blog posts ----
    for blog in Blog.objects.filter(isActive=True).values("blogLink"):
        if blog["blogLink"]:
            add_url(f"https://www.kijeka.com/blog/{blog['blogLink']}/", "0.6", "weekly")

    # ---- Categories ----
    cat_links = list(Category.objects.values("categoryLink", "categoryName"))
    for cat in cat_links:
        if cat["categoryLink"]:
            add_url(f"https://www.kijeka.com/{cat['categoryLink']}/", "0.7", "weekly")

    # ---- Subcategories ----
    for sub in SubCategory.objects.select_related("category").values(
        "subCategoryLink", "category__categoryLink"
    ):
        raw_sub_link = (sub["subCategoryLink"] or "").strip()
        cat_link = (sub["category__categoryLink"] or "").strip()
        if raw_sub_link and cat_link:
            # Sanitize: replace spaces with hyphens, lowercase
            clean_sub_link = raw_sub_link.replace(" ", "-").lower()
            add_url(
                f"https://www.kijeka.com/{cat_link}/{clean_sub_link}/",
                "0.6", "weekly"
            )

    # ---- Products ----
    product_links = list(Product.objects.values("productLink"))
    for p in product_links:
        if p["productLink"]:
            add_url(f"https://www.kijeka.com/product/{p['productLink']}/", "0.7", "monthly")

    # ---- Product x City pages (the core of Local SEO) ----
    city_slugs = list(CITY_LOCATIONS.keys())
    for p in product_links:
        if p["productLink"]:
            for city_slug in city_slugs:
                add_url(
                    f"https://www.kijeka.com/product/{p['productLink']}/{city_slug}/",
                    "0.8", "monthly"
                )

    # ---- Category x City pages ----
    for cat in cat_links:
        if cat["categoryLink"]:
            for city_slug in city_slugs:
                add_url(
                    f"https://www.kijeka.com/{cat['categoryLink']}/{city_slug}/",
                    "0.7", "monthly"
                )

    xml_parts.append("</urlset>")
    xml_content = "\n".join(xml_parts)
    return HttpResponse(xml_content, content_type="application/xml")


def redirect_to_slash_view(request, path):
    """Redirect requests for paths without trailing slashes to trailing slashes to prevent 404 mismatch."""
    query_string = request.META.get('QUERY_STRING', '')
    new_url = f"/{path}/"
    if query_string:
        new_url += f"?{query_string}"
    return redirect(new_url, permanent=True)

