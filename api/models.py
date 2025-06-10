from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):  
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')  
    role = models.CharField(max_length=500, default='', blank=True, null=True)

    def __str__(self):
        return "%s's profile" % self.user  

# Create your models here.
class Category(models.Model):
    categoryName = models.CharField(max_length=500)
    categoryLink = models.CharField(max_length=500, default='', blank=True, null=True)
    discription = models.TextField()
    metaTitle = models.CharField(max_length=500, default='', blank=True, null=True)
    metaDescription = models.CharField(max_length=500, default='', blank=True, null=True)

    def __str__(self):
        return self.categoryName

class SubCategory(models.Model):
    subCategoryName = models.CharField(max_length=500)
    subCategoryLink = models.CharField(max_length=500, default='', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    discription = models.TextField()

    def __str__(self):
        return self.subCategoryName

class Ip(models.Model):
    ip = models.CharField(max_length=500, default='', blank=True, null=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ip

class Star(models.Model):
    star = models.IntegerField()

    def __str__(self):
        return str(self.star)



class Product(models.Model):
    productName = models.CharField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subCategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, default='', blank=True, null=True)
    modelNo = models.CharField(max_length=500, default='', blank=True, null=True)
    isOnHome = models.BooleanField(default=False)
    description = models.TextField()
    images = models.ImageField(upload_to='images/')
    isUploaded = models.BooleanField(default=False)
    productLink = models.CharField(max_length=500, default='', blank=True, null=True)
    likes = models.ManyToManyField(Ip, blank=True, related_name='likes')
    star = models.ManyToManyField(Star, blank=True, related_name='Star')
    ytLink = models.CharField(max_length=20, default='', blank=True, null=True)
    productPdf = models.FileField(upload_to ='pdf/' , default='', blank=True, null=True)
    metaTitle = models.CharField(max_length=500, default='', blank=True, null=True)
    metaDescription = models.CharField(max_length=500, default='', blank=True, null=True)

    def __str__(self):
        return self.productName
    
    def total_likes(self):
        return self.likes.count()
    
    def Star_Count(self):
        return self.star.count()

    def average_star(self):
        total = 0
        for star in self.star.all():
            total += star.star
        average = 0
        if self.star.count() > 0:
            average = total / self.star.count()
        return int(average)

class ProductImage(models.Model):
      product=models.ForeignKey(Product,on_delete=models.CASCADE)    
      image1=models.ImageField(upload_to="mimages/",null=True,blank=True)
      image2=models.ImageField(upload_to="mimages/",null=True,blank=True)
      image3=models.ImageField(upload_to="mimages/",null=True,blank=True)
      image4=models.ImageField(upload_to="mimages/",null=True,blank=True)
      image5=models.ImageField(upload_to="mimages/",null=True,blank=True)
      image6=models.ImageField(upload_to="mimages/",null=True,blank=True)
      image7=models.ImageField(upload_to="mimages/",null=True,blank=True)

      def __str__(self) :
          return self.product.productName
      

class Footer(models.Model):
    mobile1 = models.CharField(max_length=500, default='', blank=True, null=True)
    isMobile1 = models.BooleanField(default=False)
    mobile2 = models.CharField(max_length=500, default='', blank=True, null=True)
    isMobile2 = models.BooleanField(default=False)
    mobile3 = models.CharField(max_length=500, default='', blank=True, null=True)
    isMobile3 = models.BooleanField(default=False)
    email1 = models.CharField(max_length=500, default='', blank=True, null=True)
    isEmail1 = models.BooleanField(default=False)
    email2 = models.CharField(max_length=500, default='', blank=True, null=True)
    isEmail2 = models.BooleanField(default=False)
    email3 = models.CharField(max_length=500, default='', blank=True, null=True)
    isEmail3 = models.BooleanField(default=False)
    addressLabel = models.CharField(max_length=500, default='', blank=True, null=True)
    aboutUsLabel = models.CharField(max_length=500, default='', blank=True, null=True)
    addressText = models.CharField(max_length=500, default='', blank=True, null=True)
    aboutUsText = models.CharField(max_length=500, default='', blank=True, null=True)
    contactLabel = models.CharField(max_length=500, default='', blank=True, null=True)

    def __str__(self):
        return self.mobile1
    
class Clients(models.Model):
    name = models.CharField(max_length=500)
    image = models.ImageField(upload_to='images/logo/')
    link = models.CharField(max_length=500, default='', blank=True, null=True)

    def __str__(self):
        return self.name
    
class YoutubeVideo(models.Model):
    title = models.CharField(max_length=500)
    videoId = models.CharField(max_length=500, default='', blank=True, null=True)
    poster = models.ImageField(upload_to='images/poster/', default='', blank=True, null=True)
    isUploaded = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class Quote(models.Model):
    quote = models.CharField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default='', blank=True, null=True)
    isMHE = models.BooleanField(default=False)

    def __str__(self):
        return self.quote


class contactUs(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=80)
    phoneNo = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    companyName = models.CharField(max_length=100)
    query = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    isSuscribed = models.BooleanField(default=False)
    isInquiry = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
class Blog(models.Model):
    #Use a callable instead, e.g., use `dict` instead of `{}`.
    def default_json():
        return dict()
    title = models.CharField(max_length=500)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    isUploaded = models.BooleanField(default=False)
    blogLink = models.CharField(max_length=500, default='', blank=True, null=True)
    author = models.CharField(max_length=500, default='', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default='', blank=True, null=True)
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(Ip, blank=True, related_name='blog_likes')
    stars = models.JSONField(default=default_json, blank=True, null=True)
    sources = models.JSONField(default=default_json, blank=True, null=True)
    image = models.ImageField(upload_to='images/blog/', default='', blank=True, null=True)
    isActive = models.BooleanField(default=False)
    isApproved = models.BooleanField(default=False)
    status = models.CharField(max_length=500, default='', blank=True, null=True)
    metaDescription = models.CharField(max_length=500, default='', blank=True, null=True)
    def __str__(self):
        return self.title


class ReachUs(models.Model):
    heading1 = models.CharField(max_length=200)
    heading2 = models.CharField(max_length=200)
    lableOfName = models.CharField(max_length=200)
    textFiledName = models.CharField(max_length=200)
    lableOfQuery = models.CharField(max_length=200)
    textFiledOfQuery = models.CharField(max_length=200)
    lableOfEmail = models.CharField(max_length=200)
    textFiledOfEmail = models.CharField(max_length=200)
    lableOfAddress = models.CharField(max_length=200)
    textFiledOfAddress = models.CharField(max_length=200)
    lableOfCountry = models.CharField(max_length=200)
    textFiledOfCountry = models.CharField(max_length=200)
    lableOfSubscription = models.CharField(max_length=200)
    lableOfCompany = models.CharField(max_length=200)
    textFiledOfCompany = models.CharField(max_length=200)
    textOfSubmit = models.CharField(max_length=200)
    labelOfPhone = models.CharField(max_length=200,default="Mobile no.")
    textFiledOfPhone = models.CharField(max_length=200,default="+91 82008xxxxx")

    def __str__(self):
        return self.heading1

class Careers(models.Model):
    jobTitle = models.CharField(max_length=200)
    jobCategory = models.CharField(max_length=200)
    requisitionNumber = models.CharField(max_length=200)
    schedule = models.CharField(max_length=200)
    discription = models.CharField(max_length=1000)
    date = models.DateTimeField()
    detailDiscription = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.jobTitle


class CareerEntry(models.Model):
    job = models.ForeignKey(Careers, on_delete=models.CASCADE)
    name = models.CharField(max_length=100) 
    email = models.CharField(max_length=80) 
    mobileNo = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    address = models.CharField(max_length=500)
    resume = models.FileField(upload_to='resumes/')

    def __str__(self):
        return self.name

class adForm(models.Model):
    name = models.CharField(max_length=30, default='')
    email = models.EmailField(blank=False)
    mobile = models.IntegerField(null=False)
    country = models.CharField(max_length=20, default='')
    company = models.CharField(max_length=20, default='')
    message = models.TextField(blank=False, default='')

    def _str_(self):
        return self.name

