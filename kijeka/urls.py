from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.urls import include, path, re_path
from django.views.static import serve
from django.views.decorators.cache import cache_control
from . import views

urlpatterns = (
    [
        re_path(
            r"^robots\.txt/?$",
            TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        ),
        re_path(
            r"^llms\.txt/?$",
            TemplateView.as_view(template_name="llms.txt", content_type="text/plain"),
        ),
        re_path(
            r"^llm\.txt/?$",
            TemplateView.as_view(template_name="llms.txt", content_type="text/plain"),
        ),
        re_path(
            r"^Kijeka_Catalogue\.pdf/?$",
            views.pdfCatalog,
            name="pdfCatalog",
        ),
        re_path(
            r"^sitemap\.xml/?$",
            views.dynamic_sitemap_view,
            name="dynamic_sitemap",
        ),
        path("admin/", admin.site.urls),
        path("api/", include("api.urls")),
        path("", views.home_view, name="home_view"),
        path("careers/", views.careers_view, name="careers_view"),
        path("about/", views.about_view, name="about_view"),
        path("blog/", views.blog_list_view, name="blog_list_view"),
        path("blog/<str:link>/", views.blogDynamic, name="blogDynamic"),
        path("contact/", views.contact_view, name="contact_view"),
        path(
            "career-details/<str:link>/",
            views.generic_index_view,
            {"title": "Career Details | Kijeka Engineers"},
            name="career_details",
        ),
        path(
            "job-apply/<str:link>/",
            views.generic_index_view,
            {"title": "Job Application | Kijeka Engineers"},
            name="job_apply",
        ),
        path("our-products/", views.our_products_view, name="our_products_view"),
        path("product/<str:link>/<str:city_slug>/", views.city_product_view, name="city_product_view"),
        path("product/<str:link>/", views.product_detail_view, name="product_detail_view"),
        path(
            "product-compare/",
            views.generic_index_view,
            {"title": "Product Comparison | Kijeka Engineers"},
            name="product_compare",
        ),
        path("privacy-policy/", views.privacy_policy_view, name="privacy_policy_view"),
        path("terms-and-condition/", views.terms_and_condition_view, name="terms_and_condition_view"),
        path("page-not-found/", views.page_not_found_view, name="page_not_found"),
        path(
            "add-to-inquiry/",
            views.generic_index_view,
            {"title": "Inquiry | Kijeka Engineers"},
            name="add_to_inquiry",
        ),
        path(
            "inquiry-form/",
            views.generic_index_view,
            {"title": "Inquiry Form | Kijeka Engineers"},
            name="inquiry_form",
        ),
        path(
            "ad/",
            views.generic_index_view,
            {"title": "Kijeka | Material Handling Equipment"},
            name="ad_page",
        ),
        path("dashboard/home/", views.dashboard, name="dashboard"),
        path("dashboard/login/", views.loginPage, name="loginPage"),
        path("dashboard/youtubevideos/", views.youtubevideos, name="youtubevideos"),
        path("dashboard/review/", views.review, name="review"),
        path("dashboard/add-products/", views.addProducts, name="addProducts"),
        path("dashboard/hot-products/", views.hotProducts, name="hotProducts"),
        path("dashboard/all-products/", views.allProducts, name="allProducts"),
        path("dashboard/clientlogos/", views.clientLogos, name="clientLogos"),
        path("dashboard/blog/", views.blog, name="blog"),
        path("dashboard/blog/newblog/", views.newBlog, name="newBlog"),
        path("dashboard/blog/drafts/", views.draftsBlog, name="draftsBlog"),
        path("dashboard/blog/reviewblog/", views.reviewBlog, name="reviewBlog"),
        path("dashboard/blog/approved/", views.approvedBlog, name="approvedBlog"),
        path("dashboard/blog/published/", views.publishedBlog, name="publishedBlog"),
        path("dashboard/blog/rejected/", views.rejectedBlog, name="rejectedBlog"),
        path("dashboard/blog/delete/", views.deleteBlog, name="deleteBlog"),
        path("dashboard/imageSlider/", views.imageSlider, name="imageSlider"),
        path("dashboard/contactdetails/", views.contactdetails, name="contactdetails"),
        path("dashboard/reachusform/", views.reachusform, name="reachusform"),
        path("dashboard/careers/", views.careers, name="careers"),
        path("products/", views.redirect_to_our_products),
        path(
            "<str:link>/<str:subLink>/",
            views.subcategory_view,
            name="subcategory_view",
        ),
        path("<str:link>/", views.category_view, name="category_view"),
    ]
    + [
        re_path(
            r"^%s(?P<path>.*)$" % settings.MEDIA_URL.lstrip("/"),
            cache_control(max_age=31536000)(serve),
            {"document_root": settings.MEDIA_ROOT},
        )
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + [
        re_path(r"^(?P<path>[^.]+[^/])$", views.redirect_to_slash_view),
        re_path(r"^.*$", views.page_not_found_view),
    ]
)

handler404 = views.handler404
