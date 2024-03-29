from django.urls import path

from . import views

urlpatterns = [
    path('addProduct/', views.addProduct, name='addProduct'),
    path('addCategory/', views.addCategory, name='addCategory'),
    path('categoryList/', views.categoryList, name='categoryList'),
    path('subCategoryList/', views.subCategoryList, name='subCategoryList'),
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
    path('quotesAdder/', views.quotesAdder, name='quotesAdder'),
    path('dataUpdater/', views.dataUpdater, name='dataUpdater'),
    path('contactus/',views.contactus,name="contactus"),
    path('inquiryform/',views.inquiryForm,name="inquiryForm"),
    path('chatbot/',views.chatbot,name="chatbot"),
    path('searchDatabase/',views.searchDatabase,name="searchDatabase"),
    path('likeProduct/',views.likeProduct,name="likeProduct"),
    path('starProduct/',views.starProduct,name="starProduct"),
    path('blogdata/',views.blogData,name="blogData"),
    path('productStar/',views.productStar,name="productStar"),
    path('imageSlider/',views.imageSlider,name="imageSlider"),
    path('addFakeLikeAndStars/',views.addFakeLikeAndStars,name="addFakeLikeAndStars"),
    path('addNewBlog/',views.addNewBlog,name="addNewBlog"),
    path('reachUsForm/',views.reachUsForm,name="reachUsForm"),
    path('contactUsForm/',views.contactUsForm,name="contactUsForm"),
    path('login/',views.loginUser,name="login"),
    path('logout/',views.logoutUser,name="logout"),
    path('inquryData/',views.inquryData,name="inquryData"),
    path('contactData/',views.contactData,name="contactData"),
    path('removeProduct/',views.removeProduct,name="removeProduct"),
    path('linksFecther/',views.linksFecther,name="linksFecther"),
    path('blogDraft/',views.blogDraft,name="blogDraft"),
    path('approvedBlogs/',views.approvedBlogs,name="approvedBlogs"),
    path('underReviewBlogs/',views.underReviewBlogs,name="underReviewBlogs"),
    path('rejectedBlogs/',views.rejectedBlogs,name="rejectedBlogs"),
    path('deletedBlogs/',views.deletedBlogs,name="deletedBlogs"),
    path('careerList/',views.careerList,name="careerList"),
    path('newCareer/',views.newCareer,name="newCareer"),
    path('jobEntry/',views.jobEntry,name="jobEntry"),
    path('userList/',views.userList,name="userList"),
    path("adForm/",views.adFormi,name="adForm"),
    path("dbDownload", views.dbDownload, name="dbDownload"),
]