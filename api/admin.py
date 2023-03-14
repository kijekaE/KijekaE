from django.contrib import admin
from .models import Category, SubCategory, Product, Clients, YoutubeVideo, Quote , contactUs,Ip
from import_export.admin import ExportActionMixin


class CategoryAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('categoryName', 'categoryLink')
    search_fields = ['categoryName', 'categoryLink']

class SubCategoryAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('subCategoryName', 'category')
    search_fields = ['subCategoryName', 'category']

class ProductAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id','productName','productLink', 'category')
    search_fields = ['id','productName','productLink', 'category__categoryName']
    list_editable = ('productName','productLink')

class ClientAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('name', 'image','link')
    search_fields = ['name', 'image','link']

class YoutubeVideoAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('title', 'videoId','poster','isUploaded')
    search_fields = ['title', 'videoId','poster','isUploaded']

class QuoteAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('quote', 'category')
    search_fields = ['quote', 'category']

class contactUsAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('name', 'email', 'query')
    search_fields = ['name', 'email', 'query']

class IpAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('ip', 'date')
    search_fields = ['ip', 'date']

# class ReviewAdmin(ExportActionMixin, admin.ModelAdmin):
#     list_display = ('client', 'product', 'review', 'rating')
#     search_fields = ['client', 'product', 'review', 'rating']

admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Clients, ClientAdmin)
admin.site.register(YoutubeVideo, YoutubeVideoAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(contactUs,contactUsAdmin)
admin.site.register(Ip,IpAdmin)

# admin.site.register(Review, ReviewAdmin)

