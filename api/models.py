from django.db import models


# Create your models here.
class Category(models.Model):
    categoryName = models.CharField(max_length=500)
    categoryLink = models.CharField(max_length=500, default='', blank=True, null=True)
    discription = models.TextField()

    def __str__(self):
        return self.categoryName

class SubCategory(models.Model):
    subCategoryName = models.CharField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    discription = models.TextField()

    def __str__(self):
        return self.subCategoryName

class Product(models.Model):
    productName = models.CharField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    modelNo = models.CharField(max_length=500, default='', blank=True, null=True)
    isOnHome = models.BooleanField(default=False)
    description = models.TextField()
    images = models.ImageField(upload_to='images/')
    isUploaded = models.BooleanField(default=False)

    def __str__(self):
        return self.productName

class Footer(models.Model):
    mobile1Label = models.CharField(max_length=500, default='', blank=True, null=True)
    isMobile1Label = models.BooleanField(default=False)
    mobile2Label = models.CharField(max_length=500, default='', blank=True, null=True)
    isMobile2Label = models.BooleanField(default=False)
    mobile3Label = models.CharField(max_length=500, default='', blank=True, null=True)
    isMobile3Label = models.BooleanField(default=False)
    email1Label = models.CharField(max_length=500, default='', blank=True, null=True)
    isEmail1Label = models.BooleanField(default=False)
    email2Label = models.CharField(max_length=500, default='', blank=True, null=True)
    isEmail2Label = models.BooleanField(default=False)
    email3Label = models.CharField(max_length=500, default='', blank=True, null=True)
    isEmail3Label = models.BooleanField(default=False)
    addressLabel = models.CharField(max_length=500, default='', blank=True, null=True)
    isaddressLabel = models.BooleanField(default=False)
    aboutUsLabel = models.CharField(max_length=500, default='', blank=True, null=True)
    isaboutUsLabel = models.BooleanField(default=False)
    contactLabel = models.CharField(max_length=500, default='', blank=True, null=True)
    iscontactLabel = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
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
    
    def __str__(self):
        return self.name