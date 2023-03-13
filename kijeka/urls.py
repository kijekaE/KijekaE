from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.urls import include, path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path("", views.index, name='index'),
    path("careers/", TemplateView.as_view(template_name='index.html')),
    path("about/", TemplateView.as_view(template_name='index.html')),
    path("blog/", TemplateView.as_view(template_name='index.html')),
    path("contact/", TemplateView.as_view(template_name='index.html')),
    path("career-details/", TemplateView.as_view(template_name='index.html')),
    path("job-apply/", TemplateView.as_view(template_name='index.html')),
    path("our-products/", TemplateView.as_view(template_name='index.html')),
    path("our-products/<str:link>/", TemplateView.as_view(template_name='index.html')),
    path("product-details/<str:link>/", TemplateView.as_view(template_name='index.html')),
    path("product-compare/", TemplateView.as_view(template_name='index.html')),
    path("privacy-policy/", TemplateView.as_view(template_name='index.html')),
    path("terms-and-condition/", TemplateView.as_view(template_name='index.html')),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

