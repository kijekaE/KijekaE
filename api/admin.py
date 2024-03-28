from django.contrib import admin
from .models import Category, SubCategory, Product, Clients, YoutubeVideo, Quote , contactUs,Ip,Blog,Star,ReachUs,Footer,Careers,CareerEntry,UserProfile
from import_export.admin import ExportActionMixin
from .models import ProductImage


class CategoryAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('categoryName', 'categoryLink')
    search_fields = ['categoryName', 'categoryLink']
    # list_display = ('categoryName', 'metaTitle','metaDescription')
    # search_fields = ['categoryName', 'metaTitle','metaDescription']
    # list_editable = ('metaTitle','metaDescription')

class SubCategoryAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('subCategoryName', 'category',"subCategoryLink")
    search_fields = ['subCategoryName', 'category',"subCategoryLink"]

class ProductAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id','productName', 'category','subCategory','isUploaded','ytLink','productPdf')
    search_fields = ['id','productName', 'category__categoryName','subCategory__subCategoryName','isUploaded','ytLink','productPdf']
    list_filter = ['isUploaded',]
    # list_display = ('id','productName', 'metaTitle','metaDescription')
    # search_fields = ['id','productName', 'metaTitle','metaDescription']
    list_editable = ('subCategory',)

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
    list_display = ('name', 'email', 'query','isInquiry')
    search_fields = ['name', 'email', 'query']
    list_editable = ('query','isInquiry',)

class IpAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('ip', 'date')
    search_fields = ['ip', 'date']

class BlogAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('title','status','isApproved','isActive')
    search_fields = ['title','status','isActive']
    list_editable = ('status','isApproved','isActive')

class StarAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('star',)
    search_fields = ['star']

class FooterAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('mobile1',)
    search_fields = ['mobile1']


class CareersAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('jobTitle','jobCategory','schedule','requisitionNumber',"date")
    search_fields = ['jobTitle','jobCategory','schedule','requisitionNumber',"date"]

class CareerEntryAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('name','email','mobileNo','country',"address")
    search_fields = ['name','email','mobileNo','country',"address"]

class UserProfileAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('user','role')
    search_fields = ['user','role']
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
admin.site.register(Blog,BlogAdmin)
admin.site.register(Star,StarAdmin)
admin.site.register(ReachUs)
admin.site.register(Footer,FooterAdmin)
admin.site.register(Careers,CareersAdmin)
admin.site.register(CareerEntry,CareerEntryAdmin)
admin.site.register(UserProfile,UserProfileAdmin)
admin.site.register(ProductImage)

# admin.site.register(Review, ReviewAdmin)

