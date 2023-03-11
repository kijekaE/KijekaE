from django.urls import path

from . import views

urlpatterns = [
    path('addProduct/', views.addProduct, name='addProduct'),
    path('addCategory/', views.addCategory, name='addCategory'),
    path('categoryList/', views.categoryList, name='categoryList'),
    path('homeCategoryList/', views.homeCategoryList, name='homeCategoryList'),
    path('categorySideBar/', views.categorySideBar, name='categorySideBar'),
    path('productList/', views.productList, name='productList'),
    path('getProductDetail/', views.getProductDetail, name='getProductDetail'),
    path('homeProductList/', views.homeProductList, name='homeProductList'),
    path('getCategoryProducts/', views.getCategoryProducts, name='getCategoryProducts'),
    path('getCategoryDescription/', views.getCategoryDescription, name='getCategoryDescription'),
    path('reviewFetcher/', views.reviewFetcher, name='reviewFetcher'),
    path('clientList/', views.clientList, name='clientList'),
    path('youtubeVideoList/', views.youtubeVideoList, name='youtubeVideoList'),
    path('quoteList/', views.quoteList, name='quoteList'),
    path('dataAdder/', views.dataAdder, name='dataAdder'),
    path('quotesAdder/', views.quotesAdder, name='quotesAdder'),
    path('dataUpdater/', views.dataUpdater, name='dataUpdater'),
    path('contactUs/',views.contactUs,name="contactUs"),
    path('chatbot/',views.chatbot,name="chatbot"),
]