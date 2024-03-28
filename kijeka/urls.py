from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.urls import include, path
from . import views

urlpatterns = [
    path("robots.txt/",TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("Kijeka_Catalogue.pdf/",views.pdfCatalog,name='pdfCatalog'),
    path("sitemap.xml/",TemplateView.as_view(template_name="sitemap.xml", content_type="application/xml")),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path("", TemplateView.as_view(template_name='index.html')),
    path("careers/", TemplateView.as_view(template_name='index.html')),
    path("about/", TemplateView.as_view(template_name='index.html')),
    path("blog/", TemplateView.as_view(template_name='index.html')),
    path("blog/<str:link>/", views.blogDynamic,name="blogDynamic"),
    path("contact/", TemplateView.as_view(template_name='index.html')),
    path("career-details/<str:link>/", TemplateView.as_view(template_name='index.html')),
    path("job-apply/<str:link>/", TemplateView.as_view(template_name='index.html')),
    path("our-products/", TemplateView.as_view(template_name='index.html')),
    path("<str:link>/", TemplateView.as_view(template_name='index.html')),
    path("product/<str:link>/", TemplateView.as_view(template_name='index.html')),
    path("product-compare/", TemplateView.as_view(template_name='index.html')),
    path("privacy-policy/", TemplateView.as_view(template_name='index.html')),
    path("terms-and-condition/", TemplateView.as_view(template_name='index.html')),
    path("dashboard/home/",views.dashboard,name="dashboard"),
    path("dashboard/login/",views.loginPage,name="loginPage"),
    path("dashboard/youtubevideos/",views.youtubevideos,name="youtubevideos"),
    path("dashboard/review/",views.review,name="review"),
    path("dashboard/add-products/",views.addProducts,name="addProducts"),
    path("dashboard/hot-products/",views.hotProducts,name="hotProducts"),
    path("dashboard/all-products/",views.allProducts,name="allProducts"),
    path("dashboard/clientlogos/",views.clientLogos,name="clientLogos"),
    path("dashboard/blog/",views.blog,name="blog"),
    path("dashboard/blog/newblog/",views.newBlog,name="newBlog"),
    path("dashboard/blog/drafts/",views.draftsBlog,name="draftsBlog"),
    path("dashboard/blog/reviewblog/",views.reviewBlog,name="reviewBlog"),
    path("dashboard/blog/approved/",views.approvedBlog,name="approvedBlog"),
    path("dashboard/blog/published/",views.publishedBlog,name="publishedBlog"),
    path("dashboard/blog/rejected/",views.rejectedBlog,name="rejectedBlog"),
    path("dashboard/blog/delete/",views.deleteBlog,name="deleteBlog"),
    path("dashboard/imageSlider/",views.imageSlider,name="imageSlider"),
    path("dashboard/contactdetails/",views.contactdetails,name="contactdetails"),
    path("dashboard/reachusform/",views.reachusform,name="reachusform"),
    path("dashboard/careers/",views.careers,name="careers"),
    path("<str:link>/", TemplateView.as_view(template_name='index.html')),
    path("<str:link>/<str:subLink>/", TemplateView.as_view(template_name='index.html')),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

