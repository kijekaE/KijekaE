from django.shortcuts import render, HttpResponse, redirect
import json
from django.views.decorators.csrf import csrf_exempt
from .models import (
    Product,
    ProductImage,
    Category,
    SubCategory,
    Clients,
    YoutubeVideo,
    Quote,
    contactUs,
    Ip,
    Blog,
    Star,
    ReachUs,
    Footer,
    Careers,
    CareerEntry,
    UserProfile,
    adForm
)
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
import random
import pandas as pd
import os
import requests
from random import randint
import urllib.parse
from difflib import SequenceMatcher
import http.client
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate, login, logout
import csv
from datetime import date


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def messageGenerator(msg, type):
    with open("bot.json") as json_data:
        dataFinal = json.load(json_data)
    data = dataFinal["type"]
    if type == "type":
        output = ""
        flag = 0
        for i in data.keys():
            if flag == 0:
                if msg.lower() in i.lower():
                    flag = 1
                    output = data[i]
                    break
                else:
                    for j in data[i].keys():
                        if flag == 0:
                            if msg.lower() in j.lower():
                                flag = 1
                                output = data[i][j]
                                break
                            else:
                                for k in data[i][j]:
                                    if flag == 0:
                                        for l in k:
                                            if flag == 0:
                                                if msg.lower() in l.lower():
                                                    flag = 1
                                                    output = k
                                                    break
                                                else:
                                                    output = "Sorry, I don't understand. For Getting Much more Precise Answer Please Select Your Interest From This Category :"
                                                    break
    else:
        data = dataFinal["questions"]
        output = "Sorry, I don't understand. For Getting Much more Precise Answer Please Select Your Interest From This Category :"
        temp = []
        for i in data.keys():
            temp.append([similar(msg.lower(), i.lower()), i])
        temp.sort(key=lambda x: x[0], reverse=True)
        if temp[0][0] > 0.3:
            output = data[temp[0][1]]
    return output


@csrf_exempt
def chatbot(request):
    if request.method == "GET":
        msg = (request.GET.get("msg")).strip()
        msgType = request.GET.get("type")
        output = messageGenerator(msg, msgType)
        if msgType != "type":
            if type(output) == str:
                output = output
            else:
                output = output[randint(0, len(output) - 1)]
            if "Precise" in output:
                with open("bot.json") as json_data:
                    dataFinal = json.load(json_data)
                data = dataFinal["type"]
                output = [output, list(data.keys())]
        else:
            if type(output) == dict:
                output = list(output.keys())
            else:
                output = output
            print(output)
        return HttpResponse(
            json.dumps({"msg": output}), content_type="application/json"
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )
  
@csrf_exempt
def addProduct(request):
    if request.method == "POST":
        productName = request.POST.get("productName")
        product = Product.objects.filter(productName=productName)
        if product.exists():#that's mean you update product info
            
            category = request.POST.get("category")
            subCategory = request.POST.get("subCategory")
            modelNo = request.POST.get("modelNo")
            isOnHome = request.POST.get("isOnHome")
            description = request.POST.get("description").replace(
                '<p data-f-id="pbf" style="text-align: center; font-size: 14px; margin-top: 30px; opacity: 0.65; font-family: sans-serif;">Powered by <a href="https://www.froala.com/wysiwyg-editor?pb=1" title="Froala Editor">Froala Editor</a></p>',
                "",
            )
            
    
            images = request.FILES.getlist("images")
            
            image_data_list = []
            productPdf = request.FILES.get("productPdf")
            for i, image in enumerate(images):
               if(i==0):
                   image_filename = f"{productName}_image_{i + 1}.jpg"
                   image_filename = image_filename.replace(' ','_')
                   with open(f"./media/images/{image_filename}", "wb") as f:
                     f.write(image.read())
            
                   image_data_list.append(f"images/{image_filename}")
               else:   
                   image_filename = f"{productName}_image_{i + 1}.jpg"
                   image_filename = image_filename.replace(' ','_')
                   with open(f"./media/mimages/{image_filename}", "wb") as f:
                     f.write(image.read())
            
                   image_data_list.append(f"mimages/{image_filename}")

            productPdf = request.FILES.get("productPdf")
            oldProduct = product.first()
           
           
            if productPdf:
                f = open(
                    "./media/pdf/" + productName + "." + str(productPdf).split(".")[-1],
                    "wb",
                )
                f.write(productPdf.read())
                f.close()
                oldProduct.productPdf = productPdf
            oldProduct.category = Category.objects.filter(categoryName=category).first()
            print(oldProduct.category)
            oldProduct.subCategory = SubCategory.objects.filter(subCategoryName=subCategory).first()
            oldProduct.modelNo = modelNo
            try:
             oldProduct.images=image_data_list[0]
            except:
             pass 
            
            if isOnHome == "true":
                oldProduct.isOnHome = True
            else:
                oldProduct.isOnHome = False
            try:
                oldProduct.ytLink = ytLink.split("https://www.youtube.com/watch?v=")[
                    1
                ].split("&")[0]
            except:
                pass
            oldProduct.description = description
            oldProduct.save()
           
            multiimg=ProductImage.objects.filter(product=oldProduct)
            if(multiimg.exists()):
               imageProduct=ProductImage.objects.get(product=oldProduct)
               if(imageProduct):
                       try:
                           
                          imageProduct.image1=image_data_list[1]
                       except:
                           imageProduct.image1=None
                       try:
                           
                          imageProduct.image2=image_data_list[2]
                       except:
                           imageProduct.image2=None
                       try:
                           
                          imageProduct.image3=image_data_list[3]
                       except:
                           imageProduct.image3=None       
                       try:
                           
                          imageProduct.image4=image_data_list[4]
                       except:
                           imageProduct.image4=None    
                       try:
                           
                          imageProduct.image5=image_data_list[5]
                       except:
                           imageProduct.image5=None
                       try:
                           
                          imageProduct.image6=image_data_list[6]
                       except:
                           imageProduct.image6=None   
                       try:
                           
                          imageProduct.image7=image_data_list[7]
                       except:
                           imageProduct.image7=None  
                       imageProduct.save()    
            else:  
                       imageProduct=ProductImage()
                       print("hello guys")
                       imageProduct.product=Product.objects.get(productName=oldProduct)
                       try:
                           
                          imageProduct.image1=image_data_list[1]
                       except:
                           imageProduct.image1=None
                       try:
                           
                          imageProduct.image2=image_data_list[2]
                       except:
                           imageProduct.image2=None
                       try:
                           
                          imageProduct.image3=image_data_list[3]
                       except:
                           imageProduct.image3=None       
                       try:
                           
                          imageProduct.image4=image_data_list[4]
                       except:
                           imageProduct.image4=None    
                       try:
                           
                          imageProduct.image5=image_data_list[5]
                       except:
                           imageProduct.image5=None
                       try:
                           
                          imageProduct.image6=image_data_list[6]
                       except:
                           imageProduct.image6=None   
                       try:
                           
                          imageProduct.image7=image_data_list[7]
                       except:
                           imageProduct.image7=None    
                       imageProduct.save()      
            
            return HttpResponse(
                json.dumps({"error": "Product already exists."}),
                content_type="application/json",
            )
        else:
            category = request.POST.get("category")
            subCategory = request.POST.get("subCategory")            
            modelNo = request.POST.get("modelNo")
            isOnHome = request.POST.get("isOnHome")
            ytLink = request.POST.get("ytLink")
            description = request.POST.get("description").replace(
                '<p data-f-id="pbf" style="text-align: center; font-size: 14px; margin-top: 30px; opacity: 0.65; font-family: sans-serif;">Powered by <a href="https://www.froala.com/wysiwyg-editor?pb=1" title="Froala Editor">Froala Editor</a></p>',
                "",
            )
            # images = request.FILES.get('images') to multiple
            images = request.FILES.getlist("images")
            image_data_list = []
            productPdf = request.FILES.get("productPdf")
            for i, image in enumerate(images):
               if(i==0):
                   image_filename = f"{productName}_image_{i + 1}.jpg"
                   image_filename = image_filename.replace(' ','_')
                   with open(f"./media/images/{image_filename}", "wb") as f:
                     f.write(image.read())
            
                   image_data_list.append(f"images/{image_filename}")
               else:   
                   image_filename = f"{productName}_image_{i + 1}.jpg"
                   image_filename = image_filename.replace(' ','_')
                   with open(f"./media/mimages/{image_filename}", "wb") as f:
                     f.write(image.read())
            
                   image_data_list.append(f"mimages/{image_filename}")

               
            print(image_data_list)    
            try:
                f = open("./media/pdf/" + productName + ".pdf", "wb")
                f.write(productPdf.read())
                f.close()
            except:
                pass
            excelSheet = request.FILES.get("excelSheet")
            if excelSheet:
                randomName = str(random.randint(100000, 999999))
                path = (
                    "./media/excels/"
                    + randomName
                    + "."
                    + str(excelSheet).split(".")[-1]
                )
                f = open(path, "wb")
                f.write(excelSheet.read())
                f.close()
                data = pd.read_excel(path)
                rows = data.shape[0]
                try:
                    for index, row in data.iterrows():
                        newProduct = Product()
                        newProduct.productName = row["Name"]
                        newProduct.category = Category.objects.filter(
                            categoryName=row["Category Name"]
                        ).first()
                        newProduct.modelNo = row["Model No"]
                        newProduct.ProductLink = (
                            row["Name"]
                            .replace(" ", "-")
                            .replace("--", "")
                            .replace("---", "")
                        )
                        if str(row["Show On Home Page"]) == "True":
                            newProduct.isOnHome = True
                        else:
                            newProduct.isOnHome = False
                        newProduct.save()
                except:
                    os.remove(path)
                    return HttpResponse(
                        json.dumps({"error": "Excel Sheet is not in correct format."}),
                        content_type="application/json",
                    )
                os.remove(path)
                return HttpResponse(
                    json.dumps({"msg": str(rows) + " products added successfully."}),
                    content_type="application/json",
                )
            else:#for no excelsheet
                newProduct = Product()
                #product_images = ProductImage.objects.filter(product=product).first()
                sub_category = SubCategory.objects.filter(subCategoryName=subCategory).first()
                if sub_category:# for subcategory
                   if images:
                    newProduct.images=image_data_list[0]
                    
                   if productPdf:
                     f = open("./media/pdf/" + productName + ".pdf", "wb")
                     f.write(productPdf.read())
                     f.close()
                     newProduct.productPdf = productPdf
                   newProduct.productName = productName
                   newProduct.category = Category.objects.filter(categoryName=category).first()
                   newProduct.subCategory = SubCategory.objects.filter(subCategoryName=subCategory).first()
                   newProduct.modelNo = modelNo
                   newProduct.productLink = (
                    productName.replace(" ", "-").replace("--", "").replace("---", "")
                   )
                   newProduct.isUploaded = True
                   try:
                     newProduct.ytLink = ytLink.split(
                        "https://www.youtube.com/watch?v="
                    )[1].split("&")[0]
                   except:
                      pass
                   if isOnHome == "true":
                      newProduct.isOnHome = True
                   else:
                      newProduct.isOnHome = False
                   newProduct.description = description.replace(
                    '<p data-f-id="pbf" style="text-align: center; font-size: 14px; margin-top: 30px; opacity: 0.65; font-family: sans-serif;">Powered by <a href="https://www.froala.com/wysiwyg-editor?pb=1" title="Froala Editor">Froala Editor</a></p>',
                    "",
                    )

                   newProduct.save()
                   
                   return HttpResponse(
                    json.dumps({"msg": "Product added successfully."}),
                    content_type="application/json",
                   )
                else:
                     if images:
                         newProduct.images=image_data_list[0]
                     if productPdf:
                       f = open("./media/pdf/" + productName + ".pdf", "wb")
                       f.write(productPdf.read())
                       f.close()
                     newProduct.productPdf = productPdf
                     newProduct.productName = productName
                     newProduct.category = Category.objects.filter(categoryName=category).first()
                     newProduct.subCategory = None
                     newProduct.modelNo = modelNo
                     newProduct.productLink = (
                     productName.replace(" ", "-").replace("--", "").replace("---", "")
                     )
                     newProduct.isUploaded = True
                     try:
                      newProduct.ytLink = ytLink.split(
                        "https://www.youtube.com/watch?v="
                     )[1].split("&")[0]
                     except:
                      pass
                     if isOnHome == "true":
                        newProduct.isOnHome = True
                     else:
                        newProduct.isOnHome = False
                     newProduct.description = description.replace(
                      '<p data-f-id="pbf" style="text-align: center; font-size: 14px; margin-top: 30px; opacity: 0.65; font-family: sans-serif;">Powered by <a href="https://www.froala.com/wysiwyg-editor?pb=1" title="Froala Editor">Froala Editor</a></p>',
                      "",
                      )

                     newProduct.save()
                     productExist = Product.objects.filter(productName=newProduct)
                     if(productExist.exists()):
                       print("new product add and multipal images is come on the way")
                       imageProduct=ProductImage()
                       print("hello guys")
                       imageProduct.product=Product.objects.get(productName=newProduct)
                       try:
                           
                          imageProduct.image1=image_data_list[1]
                       except:
                           imageProduct.image1=None
                       try:
                           
                          imageProduct.image2=image_data_list[2]
                       except:
                           imageProduct.image2=None
                       try:
                           
                          imageProduct.image3=image_data_list[3]
                       except:
                           imageProduct.image3=None       
                       try:
                           
                          imageProduct.image4=image_data_list[4]
                       except:
                           imageProduct.image4=None    
                       try:
                           
                          imageProduct.image5=image_data_list[5]
                       except:
                           imageProduct.image5=None
                       try:
                           
                          imageProduct.image6=image_data_list[6]
                       except:
                           imageProduct.image6=None   
                       try:
                           
                          imageProduct.image7=image_data_list[7]
                       except:
                           imageProduct.image7=None        
                       imageProduct.save()
                     
                     
                     return HttpResponse(
                        json.dumps({"msg": "Product added successfully."}),
                      content_type="application/json",
                     )

    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def addCategory(request):
    if request.method == "POST":
        categoryName = request.POST.get("categoryName")
        isSubCategory = request.POST.get("isSubCategory")
        category = Category.objects.filter(categoryName=categoryName)
        if category.exists():
            category = category.first()
            if isSubCategory == "true":
                subCategoryName = request.POST.get("subCategoryName")
                discription = request.POST.get("discription")
                newSubCategory = SubCategory()
                newSubCategory.subCategoryName = subCategoryName
                newSubCategory.category = category
                newSubCategory.discription = discription
                newSubCategory.subCategoryLink = subCategoryName.replace(" ", "-").lower()
                newSubCategory.save()
                return HttpResponse(
                    json.dumps({"msg": "Sub Category added successfully."}),
                    content_type="application/json",
                )
            else:
                discription = request.POST.get("discription")
                category.discription = discription
                category.save()
                return HttpResponse(
                    json.dumps({"msg": "Category edited successfully."}),
                    content_type="application/json",
                )
        else:
            discription = request.POST.get("discription")
            newCategory = Category()
            newCategory.categoryName = categoryName
            newCategory.discription = discription
            newCategory.categoryLink = categoryName.replace(" ", "-").lower()
            print(categoryName, discription)
            newCategory.save()
            return HttpResponse(
                json.dumps({"msg": "Category added successfully."}),
                content_type="application/json",
            )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def categoryList(request):
    if request.method == "GET":
        categoryList = Category.objects.all()
        categoryArr = []
        for category in categoryList:
            categoryArr.append(category.categoryName)
        return HttpResponse(
            json.dumps({"data": categoryArr}), content_type="application/json"
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )

@csrf_exempt
def subCategoryList(request):
    category = request.GET.get("category")
    category = Category.objects.filter(categoryName=category).first()
    subCategoryList = SubCategory.objects.filter(category=category).all()
    subCategoryArr = []
    for subCategory in subCategoryList:
        subCategoryArr.append(subCategory.subCategoryName)
    return HttpResponse(
        json.dumps({"data": subCategoryArr}), content_type="application/json"
    )

@csrf_exempt
def categorySideBar(request):
    if request.method == "GET":
        categoryList = Category.objects.all()
        categoryArr = []
        for category in categoryList:
            categoryArr.append([category.categoryName, category.categoryLink,[[subCategory.subCategoryName,subCategory.subCategoryLink] for subCategory in SubCategory.objects.filter(category=category).all()]])
        return HttpResponse(
            json.dumps({"data": categoryArr}), content_type="application/json"
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def productList(request):
    if request.method == "GET":
        productList = Product.objects.all()
        productArr = []
        for product in productList:
            if product.isUploaded == True:
                try:
                   productArr.append(
                    [
                        product.productName,

                        "/media/images/" + (product.images.url).split("/")[-1],
                    ]
                )
                except:
                    pass   
        return HttpResponse(
            json.dumps({"data": productArr}), content_type="application/json"
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def getCategoryDescription(request):
    if request.method == "POST":
        category = request.POST.get("category")
        category = Category.objects.filter(categoryName=category).first()
        return HttpResponse(
            json.dumps({"data": category.discription}), content_type="application/json"
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def getCategoryProducts(request):
    if request.method == "GET":
        category = request.GET.get("category")
        subCategory = request.GET.get("subCategory")
        if category == "Hot Products":
            productList = Product.objects.filter(isOnHome=True).all()
            metaTitle = "Hot Products"
            metaDescription = "Buy various Hot Products from Kijeka Engineers Pvt. Ltd."
        else:
            if subCategory == "":
                category = Category.objects.filter(categoryLink=category).first()
                metaTitle = category.metaTitle
                metaDescription = category.metaDescription
                productList = Product.objects.filter(category=category).all()
            else:
                subCategory = SubCategory.objects.filter(subCategoryLink=subCategory).first()
                metaTitle = subCategory.category.metaTitle
                metaDescription = subCategory.category.metaDescription
                productList = Product.objects.filter(subCategory=subCategory).all()
        productArr = []
        ip = get_client_ip(request)
        for product in productList:
            if product.isUploaded == True:
                liked = False
                if ip:
                    if Ip.objects.filter(ip=ip).first() == None:
                        ipNew = Ip()
                        ipNew.ip = ip
                        ipNew.save()
                    else:
                        ipNew = Ip.objects.filter(ip=ip).first()
                        if product.likes.filter(id=ipNew.id).first() != None:
                            liked = True
                averageStar = product.average_star()
                stars = int(averageStar)
                starCount = product.Star_Count()
                productArr.append(
                    [
                        product.productName,
                        (product.description)
                        .replace(
                            "<!DOCTYPE html><html><head><title></title></head><body>",
                            "",
                        )
                        .replace("</body></html>", ""),
                        "/media/images/" + (product.images.url).split("/")[-1],
                        liked,
                        product.productLink,
                        product.modelNo,
                        stars,
                        starCount,
                    ]
                )
        if len(productArr) == 0:
            return HttpResponse(
                json.dumps(
                    {"data": [["", "", ""]], "metaTitle": "", "metaDescription": ""}
                ),
                content_type="application/json",
            )
        return HttpResponse(
            json.dumps(
                {
                    "data": productArr,
                    "metaTitle": metaTitle,
                    "metaDescription": metaDescription,
                }
            ),
            content_type="application/json",
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def getProductDetail(request):
    if request.method == "GET":
        productName = request.GET.get("productName")
        product = Product.objects.filter(productLink=productName).first()
        product1 = Product.objects.filter(productName=productName).first()
        
        if product:
          product_images = ProductImage.objects.filter(product=product).filter()
        
          if product_images:
            # Get the image URLs
            product_images = ProductImage.objects.get(product=product)
            print("get object")
            
            main_img=product.images
            image1_url = product_images.image1.url if product_images.image1 else ''
            image2_url = product_images.image2.url if product_images.image2 else ''
            image3_url = product_images.image3.url if product_images.image3 else ''
            image4_url = product_images.image4.url if product_images.image4 else ''
            image5_url = product_images.image5.url if product_images.image5 else ''
            image6_url = product_images.image6.url if product_images.image6 else ''
            image7_url = product_images.image7.url if product_images.image7 else ''
            
            # Create a dictionary with the image URLs
            image_urls = {
                'main_img':"/media/images/" + (product.images.url).split("/")[-1],
                'image1_url': image1_url,
                'image2_url': image2_url,
                'image3_url': image3_url,
                'image4_url': image4_url,
                'image5_url': image5_url,
                'image6_url': image6_url,
                'image7_url': image7_url,
            }
            try:
                    image_urls["main_img"] = "/media/images/" + (product.images.url).split("/")[-1]
            except:
                    image_urls["main_img"]  = ""
          else:
            print("productImage is not exist")
            image_urls = {
                'main_img':"/media/images/" + (product.images.url).split("/")[-1],
                'image1_url': '',
                'image2_url': '',
                'image3_url': '',
                'image4_url': '',
                'image5_url': '',
                'image6_url': '',
                'image7_url': '',
            
            }
            try:
                    image_urls["main-img"] = "/media/images/" + (product.images.url).split("/")[-1]
            except:
                    image_urls["main-img"]  = ""
        # else:
        #   print("product is not exist")
        #   image_urls = {
        #     # 'main_img':"/media/images/" + (product.images.url).split("/")[-1], 
        #     'image1_url': '',
        #     'image2_url': '',
        #     'image3_url': '',
        #     'image4_url': '',
        #     'image5_url': '',
        #     'image6_url': '',
        #     'image7_url': '',
            
        #   }
        #   try:
        #             image_urls["main-img"] = "/media/images/" + (product.images.url).split("/")[-1]
        #   except:
        #             image_urls["main-img"]  = ""
        if product1:
          product_images = ProductImage.objects.filter(product=product1).filter()
        
          if product_images:
            # Get the image URLs
            product_images = ProductImage.objects.get(product=product1)
            print("get object in product1")
            
            main_img=product1.images
            image1_url = product_images.image1.url if product_images.image1 else ''
            image2_url = product_images.image2.url if product_images.image2 else ''
            image3_url = product_images.image3.url if product_images.image3 else ''
            image4_url = product_images.image4.url if product_images.image4 else ''
            image5_url = product_images.image5.url if product_images.image5 else ''
            image6_url = product_images.image6.url if product_images.image6 else ''
            image7_url = product_images.image7.url if product_images.image7 else ''
            
            # Create a dictionary with the image URLs
            image_urls = {
                'main_img':"/media/images/" + (product1.images.url).split("/")[-1],
                'image1_url': image1_url,
                'image2_url': image2_url,
                'image3_url': image3_url,
                'image4_url': image4_url,
                'image5_url': image5_url,
                'image6_url': image6_url,
                'image7_url': image7_url,
            }
            try:
                    image_urls["main-img"] = "/media/images/" + (product1.images.url).split("/")[-1]
            except:
                    image_urls["main-img"]  = ""
          else:
            print("productImage is not exist in")
            image_urls = {
                'main_img':"/media/images/" + (product1.images.url).split("/")[-1],
                'image1_url': '',
                'image2_url': '',
                'image3_url': '',
                'image4_url': '',
                'image5_url': '',
                'image6_url': '',
                'image7_url': '',
            
            }
            try:
                    image_urls["main-img"] = "/media/images/" + (product1.images.url).split("/")[-1]
            except:
                    image_urls["main-img"]  = ""
        if product == None:
            try:
                product = Product.objects.filter(productName=productName).first()
                averageStar = product.average_star()
                data = {
                    "productName": product.productName,
                    "modelNo": product.modelNo,
                    "description": str(product.description),
                    "category": product.category.categoryName,
                    "categoryLink": product.category.categoryLink,
                    "ytLink": product.ytLink,
                    "stars": int(averageStar),
                    "starCount": product.Star_Count(),
                    "isOnHome": product.isOnHome,
                    "metaTitle": product.metaTitle,
                    "metaDescription": product.metaDescription,
                    "pro_images": image_urls
                }
                try:
                    data["image"] = (
                        "/media/images/" + (product.images.url).split("/")[-1]
                    )
                except:
                    pass
                try:
                    data["productPdf"] = product.productPdf.url
                except:
                    data["productPdf"] = ""
                try:
                    data["subCategory"] =  product.subCategory.SubCategoryName
                except:
                    data["subCategory"]  = ""
                return HttpResponse(
                    json.dumps({"data": data}), content_type="application/json"
                )
            except:
                return HttpResponse(
                    json.dumps({"data": {"productName": ""}}),
                    content_type="application/json",
                )
        averageStar = product.average_star()
        data = {
            "productName": product.productName,
            "modelNo": product.modelNo,
            "description": str(product.description)
            .replace("<!DOCTYPE html><html><head><title></title></head><body>", "")
            .replace("</body></html>", ""),
            "image": "/media/images/" + (product.images.url).split("/")[-1],
            "category": product.category.categoryName,
            "categoryLink": product.category.categoryLink,
            "ytLink": product.ytLink,
            "stars": int(averageStar),
            "starCount": product.Star_Count(),
            "metaTitle": product.metaTitle,
            "metaDescription": product.metaDescription,
            "pro_images":image_urls
        }
        try:
            data["productPdf"] = product.productPdf.url
        except:
            data["productPdf"] = ""
        try:
            data["subCategory"] =  product.subCategory.subCategoryName
        except:
            data["subCategory"]  = ""
        
        return HttpResponse(json.dumps({"data": data}), content_type="application/json")
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )




@csrf_exempt
def homeProductList(request):
    if request.method == "GET":
        productList = Product.objects.filter(isOnHome=True).all()
        productArr = []
        for product in productList:
            if product.isUploaded == True:
                productArr.append(
                    [
                        product.productName,
                        "/media/images/" + (product.images.url).split("/")[-1],
                    ]
                )
        return HttpResponse(
            json.dumps({"data": productArr}), content_type="application/json"
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def homeCategoryList(request):
    if request.method == "GET":
        categoryList = Category.objects.all()
        categoryArr = []
        ip = get_client_ip(request)
        for category in categoryList:
            temp = {}
            products = Product.objects.filter(category=category).all()
            products = products[:5]
            temp["products"] = []
            for product in products:
                liked = False
                if ip:
                    if Ip.objects.filter(ip=ip).first() == None:
                        ipNew = Ip()
                        ipNew.ip = ip
                        ipNew.save()
                    else:
                        ipNew = Ip.objects.filter(ip=ip).first()
                        if product.likes.filter(id=ipNew.id).first() != None:
                            liked = True
                averageStar = product.average_star()
                stars = int(averageStar)
                starCount = product.Star_Count()
                temp["products"].append(
                    [
                        product.productName,
                        "/media/images/" + (product.images.url).split("/")[-1],
                        str(product.description)
                        .replace(
                            "<!DOCTYPE html><html><head><title></title></head><body>",
                            "",
                        )
                        .replace("</body></html>", ""),
                        liked,
                        stars,
                        starCount,
                    ]
                )
            temp["categoryName"] = category.categoryName
            temp["categoryLink"] = category.categoryLink
            temp["discription"] = category.discription
            categoryArr.append(temp)
        return HttpResponse(
            json.dumps({"data": categoryArr}), content_type="application/json"
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def reviewFetcher(request):
    if request.method == "GET":
        url = "https://www.google.com/maps/preview/review/listentitiesreviews?pb=!1m2!1y4133920741275602995!2y10276051086807358622!2m1!2i10!3e2!4m6!3b1!4b1!5b1!6b1!7b1!20b1!5m2!1s8pceZJLEOKmYseMP5M-8iA0!7e81"
        payload = {}
        headers = {
            "authority": "www.google.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,gu;q=0.8",
            "referer": "https://www.google.com/",
            "sec-ch-ua-model": "",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        temp = response.text
        temp = temp.replace(")]}'", "")
        temp = json.loads(temp)
        tempData = []
        data = []
        for i in temp:
            if str(i)[0] == "[" and tempData == []:
                tempData = i
        for i in tempData:
            if i[3] != "" and i[3] != None:
                temp = {}
                temp["name"] = i[0][1]
                temp["image"] = i[0][2].replace("br100", "br0")
                temp["time"] = i[1]
                temp["review"] = i[3]
                temp["rating"] = i[4]
                data.append(temp)
        url = "https://www.google.com/maps/preview/review/listentitiesreviews?pb=!1m2!1y4133920741275602995!2y10276051086807358622!2m1!2i10!3e1!4m6!3b1!4b1!5b1!6b1!7b1!20b1!5m2!1s8pceZJLEOKmYseMP5M-8iA0!7e81"
        response = requests.request("GET", url, headers=headers, data=payload)
        temp = response.text
        temp = temp.replace(")]}'", "")
        temp = json.loads(temp)
        tempData = []
        for i in temp:
            if str(i)[0] == "[" and tempData == []:
                tempData = i
        for i in tempData:
            if i[3] != "" and i[3] != None:
                temp = {}
                temp["name"] = i[0][1]
                temp["image"] = i[0][2].replace("br100", "br0")
                temp["time"] = i[1]
                temp["review"] = i[3]
                temp["rating"] = i[4]
                if temp not in data:
                    data.append(temp)
        return HttpResponse(json.dumps({"data": data}), content_type="application/json")
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def clientList(request):
    if request.method == "GET":
        clientList = Clients.objects.all()
        clientArr = []
        for client in clientList:
            clientArr.append(
                [
                    client.name,
                    "/media/images/logo/" + str(client.image.url).split("/")[-1],
                    client.link,
                    client.id,
                ]
            )
        clientArr.sort(key=lambda x: x[0])
        return HttpResponse(
            json.dumps({"data": clientArr}), content_type="application/json"
        )
    if request.method == "DELETE":
        id = request.GET.get("clientId")
        client = Clients.objects.filter(id=id).first()
        client.delete()
        return HttpResponse(
            json.dumps({"data": "Deleted"}), content_type="application/json"
        )
    if request.method == "POST":
        name = request.POST.get("name")
        link = request.POST.get("link")
        clId = request.POST.get("clId")
        logo = request.FILES.get("logo")
        if clId != None and clId != "":
            client = Clients.objects.filter(id=clId).first()
            client.name = name
            client.link = link
            if logo != None:
                with open(
                    "./media/images/logo/"
                    + name.replace(" ", "-").replace("---", "-").replace("--", "-")
                    + ".png",
                    "wb+",
                ) as destination:
                    for chunk in logo.chunks():
                        destination.write(chunk)
                client.image = (
                    "images/logo/"
                    + name.replace(" ", "-").replace("---", "-").replace("--", "-")
                    + ".png"
                )
            client.save()
            clientList = Clients.objects.all()
            clientArr = []
            for client in clientList:
                clientArr.append(
                    [
                        client.name,
                        "/media/images/logo/" + str(client.image.url).split("/")[-1],
                        client.link,
                        client.id,
                    ]
                )
            clientArr.sort(key=lambda x: x[0])
            return HttpResponse(
                json.dumps({"msg": "Client Updated", "data": clientArr}),
                content_type="application/json",
            )
        else:
            with open(
                "./media/images/logo/"
                + name.replace(" ", "_").replace("___", "_").replace("__", "_")
                + ".png",
                "wb+",
            ) as destination:
                for chunk in logo.chunks():
                    destination.write(chunk)
            image = (
                "images/logo/"
                + name.replace(" ", "_").replace("___", "_").replace("__", "_")
                + ".png"
            )
            client = Clients(name=name, link=link, image=image)
            client.save()
            clientList = Clients.objects.all()
            clientArr = []
            for client in clientList:
                clientArr.append(
                    [
                        client.name,
                        "/media/images/logo/" + str(client.image.url).split("/")[-1],
                        client.link,
                        client.id,
                    ]
                )
            clientArr.sort(key=lambda x: x[0])
            return HttpResponse(
                json.dumps({"msg": "Client Added", "data": clientArr}),
                content_type="application/json",
            )
        return HttpResponse(
            json.dumps({"error": "You were not supposed be here."}),
            content_type="application/json",
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def youtubeVideoList(request):
    if request.method == "GET":
        videoList = YoutubeVideo.objects.filter(isUploaded=True).all()
        videoArr = []
        for video in videoList:
            videoArr.append(
                [
                    video.title,
                    "https://www.youtube.com/embed/"
                    + video.videoId
                    + "?autoplay=0&mute=1&loop=1&showinfo=0&controls=0",
                    video.id,
                ]
            )
        return HttpResponse(
            json.dumps({"data": videoArr}), content_type="application/json"
        )
    if request.method == "POST":
        link = request.POST.get("link")
        title = request.POST.get("title")
        ytId = request.POST.get("ytId")
        if ytId == None or ytId == "":
            videoId = link.split("https://www.youtube.com/watch?v=")[1]
            newVideo = YoutubeVideo(title=title, videoId=videoId, isUploaded=True)
            newVideo.save()
            videoList = YoutubeVideo.objects.filter(isUploaded=True).all()
            videoArr = []
            for video in videoList:
                videoArr.append(
                    [
                        video.title,
                        "https://www.youtube.com/embed/"
                        + video.videoId
                        + "?autoplay=0&mute=1&loop=1&showinfo=0&controls=0",
                        video.id,
                    ]
                )
            return HttpResponse(
                json.dumps({"msg": "Video Added", "data": videoArr}),
                content_type="application/json",
            )
        else:
            video = YoutubeVideo.objects.filter(id=ytId).first()
            video.title = title
            video.videoId = link.split("https://www.youtube.com/watch?v=")[1]
            video.save()
            videoList = YoutubeVideo.objects.filter(isUploaded=True).all()
            videoArr = []
            for video in videoList:
                videoArr.append(
                    [
                        video.title,
                        "https://www.youtube.com/embed/"
                        + video.videoId
                        + "?autoplay=0&mute=1&loop=1&showinfo=0&controls=0",
                        video.id,
                    ]
                )
            return HttpResponse(
                json.dumps({"msg": "Video Updated", "data": videoArr}),
                content_type="application/json",
            )
    if request.method == "DELETE":
        videoId = request.GET.get("videoId")
        video = YoutubeVideo.objects.filter(id=videoId).first()
        video.delete()
        return HttpResponse(
            json.dumps({"msg": "Video Deleted"}), content_type="application/json"
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def quoteList(request):
    if request.method == "GET":
        categoryLink = request.GET.get("category")
        print(categoryLink)
        category = Category.objects.filter(categoryLink=categoryLink).first()
        quotes = Quote.objects.filter(category=category)
        quotesCount = quotes.count()
        if quotesCount > 0:
            quoteList = quotes.all()
            quoteArr = []
            for quote in quoteList:
                quoteArr.append(quote.quote)
            return HttpResponse(
                json.dumps({"data": quoteArr}), content_type="application/json"
            )
        else:
            quotes = Quote.objects.filter(isMHE=True).all()
            quoteArr = []
            for quote in quotes:
                quoteArr.append(quote.quote)
            return HttpResponse(
                json.dumps({"data": quoteArr}), content_type="application/json"
            )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def contactus(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phoneNo = request.POST.get("phoneNo")
        country = request.POST.get("country")
        companyName = request.POST.get("companyName")
        query = request.POST.get("query")
        address = request.POST.get("address")
        isSuscribed = request.POST.get("isSuscribed")
        contactus = contactUs()
        contactus.name = name
        contactus.email = email
        contactus.phoneNo = phoneNo
        contactus.country = country
        contactus.companyName = companyName
        contactus.query = query
        contactus.address = address
        contactus.isInquiry = False
        if isSuscribed == "on":
            isSuscribed = True
        else:
            isSuscribed = False
        contactus.isSuscribed = isSuscribed
        contactus.save()
        url = (
            "https://script.google.com/macros/s/AKfycbyRT8sZKoom_U8hfNXSDHgnu1TiN-tECDygN29OJmQXmhDdiifYEO2GGSfxQSsQYe4/exec?name="
            + name
            + "&email="
            + email
            + "&phone="
            + phoneNo
            + "&country="
            + country
            + "&company="
            + companyName
            + "&query="
            + query
            + "&address="
            + address
            + "&subject=Regarding ContactUs Form&body= "
        )
        response = requests.request("GET", url)
        return HttpResponse(
            json.dumps({"data": "success"}), content_type="application/json"
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def searchDatabase(request):
    if request.method == "GET":
        searchQuery = request.GET.get("searchQuery")
        searchQuery = searchQuery.lower()
        result = {"products": [], "categories": []}
        # search searchQuery in Product and append in result
        productsName = Product.objects.filter(productName__contains=searchQuery).all()
        productsDiscription = Product.objects.filter(
            description__contains=searchQuery
        ).all()
        productsModel = Product.objects.filter(modelNo__contains=searchQuery).all()
        for product in productsModel:
            result["products"].append(
                [
                    product.productName,
                    product.category.categoryLink,
                    (product.images.url).split("/")[-1],
                    product.productLink,
                ]
            )
        for product in productsName:
            result["products"].append(
                [
                    product.productName,
                    product.category.categoryName,
                    (product.images.url).split("/")[-1],
                    product.productLink,
                ]
            )
        for product in productsDiscription:
            result["products"].append(
                [
                    product.productName,
                    product.category.categoryLink,
                    (product.images.url).split("/")[-1],
                    product.productLink,
                ]
            )
        result = {"products": result["products"][:5], "categories": []}
        categoriesName = Category.objects.filter(
            categoryName__contains=searchQuery
        ).all()
        categoriesDiscription = Category.objects.filter(
            discription__contains=searchQuery
        ).all()
        for category in categoriesName:
            result["categories"].append([category.categoryName, category.categoryLink])
        for category in categoriesDiscription:
            result["categories"].append([category.categoryName, category.categoryLink])
        result = {
            "products": result["products"],
            "categories": result["categories"][:5],
        }
        return HttpResponse(
            json.dumps({"data": result}), content_type="application/json"
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def likeProduct(request):
    if request.method == "GET":
        productName = request.GET.get("title")
        product = Product.objects.filter(productName=productName).first()
        if product == None:
            ip = get_client_ip(request)
            if ip is not None:
                if Ip.objects.filter(ip=ip).first() == None:
                    ipNew = Ip()
                    ipNew.ip = ip
                    ipNew.save()
                ipNew = Ip.objects.filter(ip=ip).first()
                if product.likes.filter(id=ipNew.id).first() != None:
                    product.likes.remove(Ip.objects.filter(ip=ip).first())
                    product.save()
                    likes = product.total_likes()
                    return HttpResponse(
                        json.dumps({"msg": "success", "data": likes}),
                        content_type="application/json",
                    )
                else:
                    product.likes.add(Ip.objects.filter(ip=ip).first())
                    product.save()
                    likes = product.total_likes()
                    return HttpResponse(
                        json.dumps({"msg": "success", "data": likes}),
                        content_type="application/json",
                    )
                return HttpResponse(
                    json.dumps({"msg": "success"}), content_type="application/json"
                )
            else:
                return HttpResponse(
                    json.dumps({"error": "failed"}), content_type="application/json"
                )
        else:
            return HttpResponse(
                json.dumps({"error": "failed"}), content_type="application/json"
            )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def starProduct(request):
    if request.method == "GET":
        productName = request.GET.get("title")
        stars = int(request.GET.get("stars"))
        product = Product.objects.filter(productName=productName).first()
        if product:
            newStar = Star()
            newStar.star = stars
            newStar.save()
            product.star.add(newStar)
            product.save()
            data = [product.Star_Count(), product.average_star()]
            return HttpResponse(
                json.dumps({"msg": "success", "data": data}),
                content_type="application/json",
            )
        else:
            return HttpResponse(
                json.dumps({"error": "failed"}), content_type="application/json"
            )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def blogData(request):
    if request.method == "GET":
        blogList = Blog.objects.all()
        blogArr = []

        for blog in blogList:
            if blog.isActive == True and blog.isApproved == True:
                tempBlog = {}
                tempBlog["title"] = blog.title
                tempBlog["description"] = blog.description
                tempBlog["image"] = (blog.image.url).split("/")[-1]
                date = blog.date
                format_code = "%d-%m-%y"
                tempBlog["date"] = date.strftime(format_code)
                tempBlog["blogLink"] = blog.blogLink
                tempBlog["author"] = blog.author
                tempBlog["category"] = blog.category.categoryName
                tempBlog["views"] = blog.views
                # tempBlog["likes"] = len(blog.likes)
                tempBlog["sources"] = blog.sources
                blogArr.append(tempBlog)
            else:
                pass
        random.shuffle(blogArr)
        return HttpResponse(
            json.dumps({"data": blogArr}), content_type="application/json"
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def inquiryForm(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phoneNo = request.POST.get("phoneNo")
        country = request.POST.get("country")
        companyName = request.POST.get("companyName")
        address = request.POST.get("address")
        query = request.POST.get("query")
        isSuscribed = request.POST.get("isSuscribed")
        inquiryForm = contactUs()
        if isSuscribed == "on":
            isSuscribed = True
        else:
            isSuscribed = False
        inquiryForm.isSuscribed = isSuscribed
        inquiryForm.name = name
        inquiryForm.email = email
        inquiryForm.phoneNo = phoneNo
        inquiryForm.country = country
        inquiryForm.companyName = companyName
        inquiryForm.address = address
        inquiryForm.query = query
        inquiryForm.isSuscribed = isSuscribed
        inquiryForm.isInquiry = True
        inquiryForm.save()
        url = (
            "https://script.google.com/macros/s/AKfycbyRT8sZKoom_U8hfNXSDHgnu1TiN-tECDygN29OJmQXmhDdiifYEO2GGSfxQSsQYe4/exec?name="
            + name
            + "&email="
            + email
            + "&phone="
            + phoneNo
            + "&country="
            + country
            + "&company="
            + companyName
            + "&query="
            + query
            + "&address="
            + address
            + "&subject=Regarding Inquiry Form&body= "
        )
        response = requests.request("GET", url)
        return HttpResponse(
            json.dumps({"data": "success"}), content_type="application/json"
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def dataUpdater(request):
    # products = Product.objects.all()
    # for product in products:
    # product.description = product.description.replace("rgb(134, 134, 134)","rgb(0, 75, 149)").replace("518.094px", "100%")
    # product.description = product.description.replace("padding-left: 30px;","")
    # try:
    # product.description = product.description.split("<h1")[0] + product.description.split("<h1")[1].split("</h1>")[1]
    #     product.description = product.description.split('<table style="')[0] + '<div style="overflow-x: auto;"><table style="' + product.description.split('<table style="')[1].split("</table>")[0] + "</table></div>" + product.description.split("</table>")[1]
    #     print(product.productName)
    #     product.save()
    # except:
    #     pass
    # product.description = product.description.split("<h1")[0] + product.description.split("<h1")[1].split("</h1>")[1]

    # read the csv file SEO.csv
    # from difflib import SequenceMatcher
    # with open('SEO.csv', 'r') as file:
    #     reader = csv.reader(file)
    #     for row in reader:
    #         products = Product.objects.all()
    #         print(row[1])
    #         score = 0
    #         bestProduct = ""
    #         for product in products:
    #             newScore = SequenceMatcher(None, row[1], product.productName).ratio()
    #             if newScore > score:
    #                 score = newScore
    #                 bestProduct = product
    #         print(bestProduct.productName)
    #         bestProduct.metaDescription = row[3]
    #         bestProduct.metaTitle = bestProduct.productName + " in India/Gujarat/Ahmedabad"
    #         bestProduct.save()

    return HttpResponse(
        json.dumps({"msg": "Category updated successfully."}),
        content_type="application/json",
    )


@csrf_exempt
def quotesAdder(request):
    data = [
        "Drum pumps are an essential tool for the safe and efficient transfer of fluids from drums and other containers.",
        "Drum pumps are the go-to solution for handling viscous or corrosive liquids in industrial and chemical applications.",
        "Drum pumps are a versatile and cost-effective solution for transferring a wide range of fluids, from light oils to harsh chemicals.",
        "Drum pumps can significantly improve the safety and efficiency of fluid transfer operations by reducing spills, leaks, and worker exposure to hazardous materials.",
        "Drum pumps are available in a variety of materials, sizes, and styles to meet the specific needs of any application.",
        "The right drum pump can make all the difference in the safe and efficient handling of chemicals, oils, and other fluids in manufacturing and processing operations.",
        "Drum pumps are an essential component of any industrial fluid transfer operation, enabling workers to move fluids from drums and other containers with ease and precision.",
        "By using a drum pump, workers can minimize the risk of spills, leaks, and accidents during fluid transfer, ensuring a safer and more efficient work environment.",
        "Drum pumps are a critical part of any industrial or manufacturing process that involves the transfer of liquids or chemicals. The right pump can improve safety, reduce waste, and increase productivity.",
        "Drum pumps are an economical and efficient solution for transferring a wide range of fluids, offering a fast and easy way to move liquids from drums, tanks, and other containers.",
    ]
    for i in data:
        newQuote = Quote()
        newQuote.quote = i
        newQuote.category = Category.objects.filter(
            categoryName="Oil Pumps, Meters & Acces."
        ).first()
        newQuote.save()
    return HttpResponse(
        json.dumps({"msg": "data added successfully."}), content_type="application/json"
    )


@csrf_exempt
def productStar(request):
    product = Product.objects.filter(productName="Jumbo Bag Lifter").first()
    averageStar = product.average_star()
    return HttpResponse(
        json.dumps({"msg": averageStar}), content_type="application/json"
    )


@csrf_exempt
def imageSlider(request):
    if request.method == "POST":
        images = request.FILES.getlist("images")
        count = 0
        if len(images) > 0:
            for image in os.listdir("./media/images/slider/"):
                os.remove("./media/images/slider/" + image)
        for image in images:
            count += 1
            with open(
                "./media/images/slider/" + str(count) + ".jpg", "wb+"
            ) as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
        return HttpResponse(
            json.dumps({"msg": "Images Updated Successfully"}),
            content_type="application/json",
        )
    images = os.listdir("./media/images/slider")
    for i in range(len(images)):
        images[i] = "/media/images/slider/" + images[i]
    if len(images) == 0:
        return HttpResponse(json.dumps({"data": [""]}), content_type="application/json")
    return HttpResponse(json.dumps({"data": images}), content_type="application/json")


@csrf_exempt
def addFakeLikeAndStars(request):
    products = Product.objects.all()
    products = products[::-1]
    for product in products:
        stars = Star.objects.filter(star=random.randint(1, 5)).all()
        stars = stars[: random.randint(1, 20)]
        for star in stars:
            if random.randint(1, 5) % 2 == 0:
                product.star.add(star)
        product.save()
        print(product.productName)
    return HttpResponse(
        json.dumps({"msg": "data added successfully."}), content_type="application/json"
    )


@csrf_exempt
def reachUsForm(request):
    if request.method == "POST":
        title = request.POST.get("title")
        heading1 = request.POST.get("heading1")
        heading2 = request.POST.get("heading2")
        lableOfName = request.POST.get("lableOfName")
        textFiledName = request.POST.get("textFiledName")
        lableOfQuery = request.POST.get("lableOfQuery")
        textFiledOfQuery = request.POST.get("textFiledOfQuery")
        lableOfEmail = request.POST.get("lableOfEmail")
        textFiledOfEmail = request.POST.get("textFiledOfEmail")
        lableOfAddress = request.POST.get("lableOfAddress")
        textFiledOfAddress = request.POST.get("textFiledOfAddress")
        lableOfCountry = request.POST.get("lableOfCountry")
        textFiledOfCountry = request.POST.get("textFiledOfCountry")
        lableOfSubscription = request.POST.get("lableOfSubscription")
        lableOfCompany = request.POST.get("lableOfCompany")
        textFiledOfCompany = request.POST.get("textFiledOfCompany")
        textOfSubmit = request.POST.get("textOfSubmit")
        labelOfPhone = request.POST.get("labelOfPhone")
        textFiledOfPhone = request.POST.get("textFiledOfPhone")
        reachus = ReachUs.objects.first()
        reachus.heading1 = heading1
        reachus.heading2 = heading2
        reachus.lableOfName = lableOfName
        reachus.textFiledName = textFiledName
        reachus.lableOfQuery = lableOfQuery
        reachus.textFiledOfQuery = textFiledOfQuery
        reachus.lableOfEmail = lableOfEmail
        reachus.textFiledOfEmail = textFiledOfEmail
        reachus.lableOfAddress = lableOfAddress
        reachus.textFiledOfAddress = textFiledOfAddress
        reachus.lableOfCountry = lableOfCountry
        reachus.textFiledOfCountry = textFiledOfCountry
        reachus.lableOfSubscription = lableOfSubscription
        reachus.lableOfCompany = lableOfCompany
        reachus.textFiledOfCompany = textFiledOfCompany
        reachus.textOfSubmit = textOfSubmit
        reachus.labelOfPhone = labelOfPhone
        reachus.textFiledOfPhone = textFiledOfPhone
        reachus.save()
        return HttpResponse(
            json.dumps({"msg": "Data updated successfully."}),
            content_type="application/json",
        )
    data = {}
    reachus = ReachUs.objects.first()
    data["heading1"] = reachus.heading1
    data["heading2"] = reachus.heading2
    data["lableOfName"] = reachus.lableOfName
    data["textFiledName"] = reachus.textFiledName
    data["lableOfQuery"] = reachus.lableOfQuery
    data["textFiledOfQuery"] = reachus.textFiledOfQuery
    data["lableOfEmail"] = reachus.lableOfEmail
    data["textFiledOfEmail"] = reachus.textFiledOfEmail
    data["lableOfAddress"] = reachus.lableOfAddress
    data["textFiledOfAddress"] = reachus.textFiledOfAddress
    data["lableOfCountry"] = reachus.lableOfCountry
    data["textFiledOfCountry"] = reachus.textFiledOfCountry
    data["lableOfSubscription"] = reachus.lableOfSubscription
    data["lableOfCompany"] = reachus.lableOfCompany
    data["textFiledOfCompany"] = reachus.textFiledOfCompany
    data["textOfSubmit"] = reachus.textOfSubmit
    data["labelOfPhone"] = reachus.labelOfPhone
    data["textFiledOfPhone"] = reachus.textFiledOfPhone
    return HttpResponse(json.dumps({"data": data}), content_type="application/json")


@csrf_exempt
def contactUsForm(request):
    if request.method == "POST":
        addressLabel = request.POST.get("addressLabel")
        aboutUsLabel = request.POST.get("aboutUsLabel")
        contactLabel = request.POST.get("contactLabel")
        addressText = request.POST.get("addressText")
        aboutUsText = request.POST.get("aboutUsText")
        mobile1 = request.POST.get("mobile1")
        email1 = request.POST.get("email1")
        mobile2 = request.POST.get("mobile2")
        email2 = request.POST.get("email2")
        mobile3 = request.POST.get("mobile3")
        email3 = request.POST.get("email3")
        if request.POST.get("isMobile1") == "true":
            isMobile1 = True
        else:
            isMobile1 = False
        if request.POST.get("isEmail1") == "true":
            isEmail1 = True
        else:
            isEmail1 = False
        if request.POST.get("isMobile2") == "true":
            isMobile2 = True
        else:
            isMobile2 = False
        if request.POST.get("isEmail2") == "true":
            isEmail2 = True
        else:
            isEmail2 = False
        if request.POST.get("isMobile3") == "true":
            isMobile3 = True
        else:
            isMobile3 = False
        if request.POST.get("isEmail3") == "true":
            isEmail3 = True
        else:
            isEmail3 = False
        footer = Footer.objects.first()
        footer.addressLabel = addressLabel
        footer.aboutUsLabel = aboutUsLabel
        footer.contactLabel = contactLabel
        footer.addressText = addressText
        footer.aboutUsText = aboutUsText
        footer.mobile1 = mobile1
        footer.email1 = email1
        footer.mobile2 = mobile2
        footer.email2 = email2
        footer.mobile3 = mobile3
        footer.email3 = email3
        footer.isMobile1 = isMobile1
        footer.isEmail1 = isEmail1
        footer.isMobile2 = isMobile2
        footer.isEmail2 = isEmail2
        footer.isMobile3 = isMobile3
        footer.isEmail3 = isEmail3
        footer.save()
        return HttpResponse(
            json.dumps({"msg": "Data updated successfully."}),
            content_type="application/json",
        )
    data = {}
    footer = Footer.objects.first()
    data["contactLabel"] = footer.contactLabel
    data["addressLabel"] = footer.addressLabel
    data["aboutUsLabel"] = footer.aboutUsLabel
    data["addressText"] = footer.addressText
    data["aboutUsText"] = footer.aboutUsText
    data["mobile1"] = footer.mobile1
    data["mobile2"] = footer.mobile2
    data["mobile3"] = footer.mobile3
    data["email1"] = footer.email1
    data["email2"] = footer.email2
    data["email3"] = footer.email3
    data["isMobile1"] = footer.isMobile1
    data["isEmail1"] = footer.isEmail1
    data["isMobile2"] = footer.isMobile2
    data["isEmail2"] = footer.isEmail2
    data["isMobile3"] = footer.isMobile3
    data["isEmail3"] = footer.isEmail3
    return HttpResponse(json.dumps({"data": data}), content_type="application/json")


@csrf_exempt
def loginUser(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("/dashboard/home/")
            else:
                return HttpResponse(
                    json.dumps({"error": "Your account is not active."}),
                    content_type="application/json",
                )
        else:
            return HttpResponse(
                json.dumps({"error": "Invalid username or password."}),
                content_type="application/json",
            )
    return HttpResponse(
        json.dumps({"error": "You were not supposed to be here."}),
        content_type="application/json",
    )


@csrf_exempt
def logoutUser(request):
    logout(request)
    return redirect("/dashboard/login/")


@csrf_exempt
def inquryData(request):
    if request.method == "GET":
        curentUser = request.GET.get("user")
        user = User.objects.filter(username=curentUser).first()
        try:
            role = UserProfile.objects.filter(user=user).first().role
        except:
            role = "admin"
        inquryList = contactUs.objects.filter(isInquiry=True).all()
        inquryList = list(inquryList.values())
        inquryList = inquryList[::-1]
        return HttpResponse(
            json.dumps({"data": inquryList, "role": role}),
            content_type="application/json",
        )
    if request.method == "DELETE":
        id = request.GET.get("id")
        contactUs.objects.filter(id=id).delete()
        return HttpResponse(
            json.dumps({"msg": "Data deleted successfully."}),
            content_type="application/json",
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed to be here."}),
        content_type="application/json",
    )


@csrf_exempt
def contactData(request):
    if request.method == "GET":
        curentUser = request.GET.get("user")
        user = User.objects.filter(username=curentUser).first()
        try:
            role = UserProfile.objects.filter(user=user).first().role
        except:
            role = "admin"
        contactList = contactUs.objects.filter(isInquiry=False).all()
        contactList = list(contactList.values())
        contactList = contactList[::-1]
        return HttpResponse(
            json.dumps({"data": contactList}), content_type="application/json"
        )
    if request.method == "DELETE":
        id = request.GET.get("id")
        contactUs.objects.filter(id=id).delete()
        return HttpResponse(
            json.dumps({"msg": "Data deleted successfully."}),
            content_type="application/json",
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed to be here."}),
        content_type="application/json",
    )


@csrf_exempt
def removeProduct(request):
    if request.method == "DELETE":
        name = request.GET.get("name")
        productF = Product.objects.filter(productName=name).first()
        if(productF):
          productF.isUploaded = False
        productF.save()
        return HttpResponse(
            json.dumps({"msg": "Data deleted successfully."}),
            content_type="application/json",
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed to be here."}),
        content_type="application/json",
    )


@csrf_exempt
def linksFecther(request):
    blogs = Blog.objects.all()
    urls = []
    for blog in blogs:
        print(blog.blogLink)
        urls.append("/" + blog.blogLink)
    return HttpResponse(json.dumps({"urls": urls}), content_type="application/json")


@csrf_exempt
def addNewBlog(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        sources = request.POST.get("sources")
        author = request.POST.get("author")
        category = request.POST.get("category")
        categoryObj = Category.objects.filter(categoryName=category).first()
        image = request.FILES.get("image")
        f = open("./media/images/blog/" + title + ".jpg", "wb")
        f.write(image.read())
        f.close()
        description = request.POST.get("edit")
        blog = Blog()
        blog.title = title
        blog.description = description
        blog.blogLink = title.replace(" ", "-").replace("&", "and").lower()
        blog.isUploaded = True
        blog.sources = sources
        blog.author = author
        blog.category = categoryObj
        blog.image = image
        blog.isActive = True
        blog.isApproved = False
        blog.status = "draft"
        blog.description = description
        blog.save()
        return HttpResponse(
            json.dumps({"data": "success"}), content_type="application/json"
        )

    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def blogDraft(request):
    if request.method == "GET":
        blogList = Blog.objects.filter(status="draft").all()
        blogArr = []

        for blog in blogList:
            if blog.isActive == True:
                tempBlog = {}
                tempBlog["id"] = blog.id
                tempBlog["title"] = blog.title
                tempBlog["description"] = blog.description
                tempBlog["image"] = blog.image.url
                date = blog.date
                format_code = "%d-%m-%y"
                tempBlog["date"] = date.strftime(format_code)
                tempBlog["blogLink"] = blog.blogLink
                tempBlog["author"] = blog.author
                tempBlog["category"] = blog.category.categoryName
                tempBlog["views"] = blog.views
                tempBlog["sources"] = blog.sources
                blogArr.append(tempBlog)
            else:
                pass
        return HttpResponse(
            json.dumps({"data": blogArr}), content_type="application/json"
        )
    if request.method == "DELETE":
        id = request.GET.get("id")
        blogSeleted = Blog.objects.filter(id=id).first()
        blogSeleted.isActive = False
        blogSeleted.isApproved = False
        blogSeleted.status = "deleted"
        blogSeleted.save()
        return HttpResponse(
            json.dumps({"msg": "Data deleted successfully."}),
            content_type="application/json",
        )
    if request.method == "POST":
        id = request.POST.get("id")
        status = request.POST.get("status")
        blogSeleted = Blog.objects.filter(id=id).first()
        blogSeleted.isActive = True
        blogSeleted.status = status
        blogSeleted.save()
        return HttpResponse(
            json.dumps({"msg": "Data updated  successfully."}),
            content_type="application/json",
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def approvedBlogs(request):
    if request.method == "GET":
        blogList = Blog.objects.filter(isApproved=True).all()
        blogArr = []

        for blog in blogList:
            if blog.isActive == True and blog.isApproved == True:
                tempBlog = {}
                tempBlog["id"] = blog.id
                tempBlog["title"] = blog.title
                tempBlog["description"] = blog.description
                tempBlog["image"] = blog.image.url
                date = blog.date
                format_code = "%d-%m-%y"
                tempBlog["date"] = date.strftime(format_code)
                tempBlog["blogLink"] = blog.blogLink
                tempBlog["author"] = blog.author
                tempBlog["category"] = blog.category.categoryName
                tempBlog["views"] = blog.views
                # tempBlog["likes"] = len(blog.likes)
                tempBlog["sources"] = blog.sources
                blogArr.append(tempBlog)

            else:
                pass
        return HttpResponse(
            json.dumps({"data": blogArr}), content_type="application/json"
        )

    if request.method == "DELETE":
        id = request.GET.get("id")
        blogSeleted = Blog.objects.filter(id=id).first()
        blogSeleted.isActive = False
        blogSeleted.isApproved = False
        blogSeleted.status = "deleted"
        blogSeleted.save()
        return HttpResponse(
            json.dumps({"msg": "Data deleted successfully."}),
            content_type="application/json",
        )

    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def underReviewBlogs(request):
    if request.method == "GET":
        blogList = Blog.objects.filter(status="review").all()
        blogArr = []
        for blog in blogList:
            if blog.isActive == True:
                tempBlog = {}
                tempBlog["id"] = blog.id
                tempBlog["title"] = blog.title
                tempBlog["description"] = blog.description
                tempBlog["image"] = blog.image.url
                date = blog.date
                format_code = "%d-%m-%y"
                tempBlog["date"] = date.strftime(format_code)
                tempBlog["blogLink"] = blog.blogLink
                tempBlog["author"] = blog.author
                tempBlog["category"] = blog.category.categoryName
                tempBlog["views"] = blog.views
                # tempBlog["likes"] = len(blog.likes)
                tempBlog["sources"] = blog.sources
                blogArr.append(tempBlog)

            else:
                pass
        return HttpResponse(
            json.dumps({"data": blogArr}), content_type="application/json"
        )
    if request.method == "DELETE":
        id = request.GET.get("id")
        blogSeleted = Blog.objects.filter(id=id).first()
        blogSeleted.isActive = False
        blogSeleted.isApproved = False
        blogSeleted.status = "deleted"
        blogSeleted.save()
        return HttpResponse(
            json.dumps({"msg": "Data deleted successfully."}),
            content_type="application/json",
        )

    if request.method == "POST":
        id = request.POST.get("id")
        status = request.POST.get("status")
        blogSeleted = Blog.objects.filter(id=id).first()
        if status == "approved":
            blogSeleted.isApproved = True
        blogSeleted.isActive = True
        blogSeleted.status = status
        blogSeleted.save()
        return HttpResponse(
            json.dumps({"msg": "Data approved successfully."}),
            content_type="application/json",
        )

    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def rejectedBlogs(request):
    if request.method == "GET":
        blogList = Blog.objects.filter(status="rejected").all()
        blogArr = []

        for blog in blogList:
            if blog.isActive == True:
                tempBlog = {}
                tempBlog["id"] = blog.id
                tempBlog["title"] = blog.title
                tempBlog["description"] = blog.description
                tempBlog["image"] = blog.image.url
                date = blog.date
                format_code = "%d-%m-%y"
                tempBlog["date"] = date.strftime(format_code)
                tempBlog["blogLink"] = blog.blogLink
                tempBlog["author"] = blog.author
                tempBlog["category"] = blog.category.categoryName
                tempBlog["views"] = blog.views
                # tempBlog["likes"] = len(blog.likes)
                tempBlog["sources"] = blog.sources
                blogArr.append(tempBlog)

            else:
                pass
        return HttpResponse(
            json.dumps({"data": blogArr}), content_type="application/json"
        )

    if request.method == "DELETE":
        id = request.GET.get("id")
        blogSeleted = Blog.objects.filter(id=id).first()
        blogSeleted.isActive = False
        blogSeleted.isApproved = False
        blogSeleted.status = "deleted"
        blogSeleted.save()
        return HttpResponse(
            json.dumps({"msg": "Data deleted successfully."}),
            content_type="application/json",
        )

    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def deletedBlogs(request):
    if request.method == "GET":
        blogList = Blog.objects.filter(status="deleted")
        blogArr = []

        for blog in blogList:
            if blog.isActive == False:
                tempBlog = {}
                tempBlog["id"] = blog.id
                tempBlog["title"] = blog.title
                tempBlog["description"] = blog.description
                tempBlog["image"] = blog.image.url
                date = blog.date
                format_code = "%d-%m-%y"
                tempBlog["date"] = date.strftime(format_code)
                tempBlog["blogLink"] = blog.blogLink
                tempBlog["author"] = blog.author
                tempBlog["category"] = blog.category.categoryName
                tempBlog["views"] = blog.views
                # tempBlog["likes"] = len(blog.likes)
                tempBlog["sources"] = blog.sources
                blogArr.append(tempBlog)

            else:
                pass
        return HttpResponse(
            json.dumps({"data": blogArr}), content_type="application/json"
        )

    if request.method == "DELETE":
        id = request.GET.get("id")
        blogSeleted = Blog.objects.filter(id=id).first()
        blogSeleted.isActive = False
        blogSeleted.isApproved = False
        blogSeleted.status = "removed"
        blogSeleted.save()
        return HttpResponse(
            json.dumps({"msg": "Data deleted successfully."}),
            content_type="application/json",
        )

    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def careerList(request):
    if request.method == "GET":
        careers = Careers.objects.order_by("requisitionNumber").all()
        careerArr = list(careers.values())
        for career in careerArr:
            career["applied"] = 20
            career["date"] = career["date"].strftime("%d-%m-%Y")
        return HttpResponse(
            json.dumps({"data": careerArr}), content_type="application/json"
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def newCareer(request):
    if request.method == "POST":
        jobtitle = request.POST.get("jobtitle")
        jobCategory = request.POST.get("jobCategory")
        requisitionNumber = request.POST.get("requisitionNumber")
        schedule = request.POST.get("schedule")
        description = request.POST.get("edit")
        simpledescription = request.POST.get("simpledescription")
        career = Careers()
        career.jobTitle = jobtitle
        career.jobCategory = jobCategory
        career.requisitionNumber = requisitionNumber
        career.schedule = schedule
        career.discription = simpledescription
        career.detailDiscription = description
        career.date = date.today()
        career.save()
        return HttpResponse(
            json.dumps({"data": "Data added successfully"}),
            content_type="application/json",
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )


@csrf_exempt
def jobEntry(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        number = request.POST.get("number")
        country = request.POST.get("country")
        address = request.POST.get("address")
        resume = request.FILES.get("resume")
        requisitionNumber = request.POST.get("requisitionNumber")

        careers = Careers.objects.filter(requisitionNumber=requisitionNumber).first()
        if resume:
            f = open("./media/resumes/" + name + "." + str(resume).split(".")[-1], "wb")
            f.write(resume.read())
            f.close()

        careerentry = CareerEntry()
        careerentry.job = careers
        careerentry.name = name
        careerentry.email = email
        careerentry.mobileNo = number
        careerentry.country = country
        careerentry.address = address
        careerentry.resume = resume

        careerentry.save()
        return HttpResponse(
            json.dumps({"data": "Data added successfully"}),
            content_type="application/json",
        )
    return HttpResponse(
        json.dumps({"error": "You were not supposed be here."}),
        content_type="application/json",
    )

@csrf_exempt
def userList(request):
    if request.method =="GET":
        userlist = UserProfile.objects.all()
        userdata = []
        for user in userlist:
            temp = {}
            temp["id"] = user.user.id
            temp["firstName"] = user.user.first_name
            temp["lastName"] = user.user.last_name 
            temp["email"] = user.user.email  
            temp["role"] = user.role
            if user.role == "admin":
                temp["access"] = "Home, Blog, Products, Image Slider, Youtube Videos, Client Logos, Careers, Reach US Form, Contact Details, Users"
            elif user.role == "inquiry":
                temp["access"] = "Home, Careers"
            else:
                temp["access"] = "Home, Blog"
            userdata.append(temp)
        return HttpResponse(
                json.dumps({"data":userdata}),content_type="application/json",)

    if request.method == "POST":
        firstName = request.POST.get("firstName")
        lastName = request.POST.get("lastName")
        email = request.POST.get("email")
        role = request.POST.get("role")
        userId = request.POST.get("userId")
        if userId != "":
            userobj = User.objects.filter(id=userId).first()
            if userobj:
                userobj.first_name = firstName
                userobj.last_name = lastName
                userobj.email = email
                userprofile = UserProfile.objects.filter(user = userobj).first()
                userprofile.role = role
                userobj.save()
                userprofile.save()
                return HttpResponse(json.dumps({"msg": "Data updated successfully"}),content_type="application/json",)
        else:
            try:
                newUser = User() 
                newUser.email = email
                newUser.username = email
                newUser.first_name = firstName
                newUser.last_name = lastName
                newUser.save()

                userprofile = UserProfile()
                userprofile.user = newUser
                userprofile.role = role
                userprofile.save()
                return HttpResponse(json.dumps({"msg": "Data added successfully"}),content_type="application/json")
            except Exception as e:
                return HttpResponse(json.dumps({"error": str(e)}),content_type="application/json")
    

    if request.method == "DELETE":
        userId = request.GET.get("userId")
        try:
            userobj = User.objects.filter(id=int(userId)).first()
            userobj.delete()
            return HttpResponse(json.dumps({"msg": "Deleted"}), content_type="application/json")
        except Exception as e:
            return HttpResponse(json.dumps({"error": str(e)}), content_type="application/json")
            
@csrf_exempt
def adFormi(request):
    if request.method == "POST":
        inquiryform = adForm()
        inquiryform.name = request.POST.get('name')
        inquiryform.email = request.POST.get('email')
        inquiryform.mobile = request.POST.get('mobile')
        inquiryform.country = request.POST.get('country')
        inquiryform.company = request.POST.get('company')
        inquiryform.message = request.POST.get('message')
        inquiryform.save()
        return HttpResponse(json.dumps({"msg" : "Success"}))
    else:
        return HttpResponse(json.dumps({"msg" : "Bad request"}))

@csrf_exempt
def dbDownload(request):
    if request.user.is_superuser:
        # copy the database file to the static folder
        os.system("cp db.sqlite3 static/")
        return HttpResponse("<a href='/static/db.sqlite3' download>Download</a>")