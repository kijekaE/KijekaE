from django.shortcuts import render, HttpResponse, redirect
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Category, SubCategory, Clients,YoutubeVideo, Quote,contactUs,Ip
from django.core.files.storage import FileSystemStorage
import random
import pandas as pd
import os
import requests
from random import randint
from difflib import SequenceMatcher

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def messageGenerator(msg,type):
    with open('bot.json') as json_data:
        dataFinal = json.load(json_data)
    data = dataFinal['type']
    if type == 'type':
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
        data = dataFinal['questions']
        output = "Sorry, I don't understand. For Getting Much more Precise Answer Please Select Your Interest From This Category :"
        temp = []
        for i in data.keys():
            temp.append([similar(msg.lower(),i.lower()),i])
        temp.sort(key=lambda x: x[0], reverse=True)
        if temp[0][0] > 0.3:
            output = data[temp[0][1]]
    return output

@csrf_exempt
def chatbot(request):
    if request.method == 'GET':
        msg = (request.GET.get('msg')).strip()
        msgType = request.GET.get('type')
        output = messageGenerator(msg,msgType)
        if msgType != 'type':
            if type(output) == str:
                output = output
            else:
                output = output[randint(0,len(output)-1)]
            if "Precise" in output:
                with open('bot.json') as json_data:
                    dataFinal = json.load(json_data)
                data = dataFinal['type']
                output = [output,list(data.keys())]
        else:
            if type(output) == dict:
                output = list(output.keys())
            else:
                output = output
            print(output)
        return HttpResponse(json.dumps({'msg': output}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def addProduct(request):
    if request.method == 'POST':
        productName = request.POST.get('productName')
        product = Product.objects.filter(productName=productName)
        if  product.exists():
            category = request.POST.get('category')
            modelNo = request.POST.get('modelNo')
            isOnHome = request.POST.get('isOnHome')
            description = request.POST.get('description')
            images = request.FILES.get('images')
            oldProduct = product.first()
            if images:
                f = open("./media/images/"+productName +"."+ str(images).split(".")[-1], 'wb')
                f.write(images.read())
                f.close()
            oldProduct.category = Category.objects.filter(categoryName=category).first()
            oldProduct.modelNo = modelNo
            if isOnHome == 'true':
                oldProduct.isOnHome = True
            else:
                oldProduct.isOnHome = False
            oldProduct.description = description
            oldProduct.images = images
            oldProduct.save()
            return HttpResponse(json.dumps({'error': 'Product already exists.'}), content_type='application/json')
        else :
            category = request.POST.get('category')
            modelNo = request.POST.get('modelNo')
            isOnHome = request.POST.get('isOnHome')
            description = request.POST.get('description')
            # images = request.FILES.get('images') to multiple
            images = request.FILES.get('images')
            f = open("./media/images/"+productName +".png", 'wb')
            f.write(images.read())
            f.close()
            excelSheet = request.FILES.get('excelSheet')
            if excelSheet:
                randomName = str(random.randint(100000, 999999))
                path = "./media/excels/"+randomName+"."+str(excelSheet).split(".")[-1]
                f = open(path, 'wb') 
                f.write(excelSheet.read())
                f.close()
                data = pd.read_excel(path)
                rows = data.shape[0]
                try:
                    for index, row in data.iterrows():
                        newProduct = Product()
                        newProduct.productName = row['Name']
                        newProduct.category = Category.objects.filter(categoryName=row['Category Name']).first()
                        newProduct.modelNo = row['Model No']
                        if str(row['Show On Home Page']) == 'True':
                            newProduct.isOnHome = True
                        else:
                            newProduct.isOnHome = False
                        newProduct.save()
                except:
                    os.remove(path)
                    return HttpResponse(json.dumps({'error': 'Excel Sheet is not in correct format.'}), content_type='application/json')
                os.remove(path)
                return HttpResponse(json.dumps({'msg': str(rows) + ' products added successfully.'}), content_type='application/json')
            else:
                if images:
                    print("./media/images/"+productName +".png")
                    f = open("./media/images/"+productName +".png", 'wb')
                    f.write(images.read())
                    f.close()
                newProduct = Product()
                newProduct.productName = productName
                newProduct.category = Category.objects.filter(categoryName=category).first()
                newProduct.modelNo = modelNo
                if isOnHome == 'true':
                    newProduct.isOnHome = True
                else:
                    newProduct.isOnHome = False
                newProduct.description = description
                print(description)
                newProduct.images = images
                newProduct.save()
                return HttpResponse(json.dumps({'msg': 'Product added successfully.'}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def addCategory(request):
    if request.method == 'POST':
        categoryName = request.POST.get('categoryName')
        isSubCategory = request.POST.get('isSubCategory')
        category = Category.objects.filter(categoryName=categoryName)
        if category.exists():
            category = category.first()
            if isSubCategory == 'true':
                subCategoryName = request.POST.get('subCategoryName')
                discription = request.POST.get('discription')
                newSubCategory = SubCategory()
                newSubCategory.subCategoryName = subCategoryName
                newSubCategory.category = category
                newSubCategory.discription = discription
                newSubCategory.save()
                return HttpResponse(json.dumps({'msg': 'Sub Category added successfully.'}), content_type='application/json')
            else:
                discription = request.POST.get('discription')
                category.discription = discription
                category.save()
                return HttpResponse(json.dumps({'msg': 'Category edited successfully.'}), content_type='application/json')
        else:
            discription = request.POST.get('discription')
            newCategory = Category()
            newCategory.categoryName = categoryName
            newCategory.discription = discription
            newCategory.categoryLink = categoryName.replace(" ", "-").lower()
            print(categoryName, discription)
            newCategory.save()
            return HttpResponse(json.dumps({'msg': 'Category added successfully.'}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def categoryList(request):
    if request.method == 'GET':
        categoryList = Category.objects.all()
        categoryArr = []
        for category in categoryList:
            categoryArr.append(category.categoryName)
        return HttpResponse(json.dumps({'data': categoryArr}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def categorySideBar(request):
    if request.method == 'GET':
        categoryList = Category.objects.all()
        categoryArr = []
        for category in categoryList:
            categoryArr.append([category.categoryName,category.categoryLink])
        return HttpResponse(json.dumps({'data': categoryArr}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def productList(request):
    if request.method == 'GET':
        productList = Product.objects.all()
        productArr = []
        for product in productList:
            productArr.append([product.productName,"/media/images/"+(product.images.url).split("/")[-1]])
        return HttpResponse(json.dumps({'data': productArr}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def getCategoryDescription(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        print(category)
        category = Category.objects.filter(categoryName=category).first()
        return HttpResponse(json.dumps({'data': category.discription}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def getCategoryProducts(request):
    if request.method == 'GET':
        category = request.GET.get('category')
        if category == "Hot Products":
            productList = Product.objects.filter(isOnHome=True).all()
        else:
            category = Category.objects.filter(categoryLink=category).first()
            productList = Product.objects.filter(category=category).all()
        productArr = []
        ip = get_client_ip(request)
        for product in productList:
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
            productArr.append([product.productName,(product.description).replace("<!DOCTYPE html><html><head><title></title></head><body>","").replace("</body></html>",""),"/media/images/"+(product.images.url).split("/")[-1],liked,product.productLink,product.modelNo])
        if len(productArr) == 0:
            return HttpResponse(json.dumps({'data': [["","",""]]}), content_type='application/json')
        return HttpResponse(json.dumps({'data': productArr}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def translateData(request):
    if request.method == 'GET':
        language = request.GET.get('language')
        data = request.GET.get('data')
        url = "https://translate.googleapis.com/translate_a/t?anno=3&client=te&format=html&v=1.0&key&logld=vTE_20230312&sl=en&tl="+language+"&tc=1&sr=1&tk=533754.997732"
        payload=data
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        return HttpResponse(json.dumps({'data': response.t}), content_type='application/json')
    


@csrf_exempt
def getProductDetail(request):
    if request.method == 'GET':
        productName = request.GET.get('productName')
        product = Product.objects.filter(productLink=productName).first()
        data = {
            'productName': product.productName,
            'modelNo': product.modelNo,
            'description': str(product.description).replace("<!DOCTYPE html><html><head><title></title></head><body>","").replace("</body></html>",""),
            'image': "/media/images/"+(product.images.url).split("/")[-1],
            'category': product.category.categoryName,
            'categoryLink': product.category.categoryLink
        }
        return HttpResponse(json.dumps({'data': data}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def homeProductList(request):
    if request.method == 'GET':
        productList = Product.objects.filter(isOnHome=True).all()
        productArr = []
        for product in productList:
            productArr.append([product.productName,"/media/images/"+(product.images.url).split("/")[-1]])
        return HttpResponse(json.dumps({'data': productArr}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def homeCategoryList(request):
    if request.method == 'GET':
        categoryList = Category.objects.all()
        categoryArr = []
        ip = get_client_ip(request)
        for category in categoryList:
            temp = {}
            products = Product.objects.filter(category=category).all()
            products = products[:5]
            temp["products"]  = []
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
                temp["products"].append([product.productName,"/media/images/"+(product.images.url).split("/")[-1],str(product.description).replace("<!DOCTYPE html><html><head><title></title></head><body>","").replace("</body></html>",""),liked])
            temp["categoryName"] = category.categoryName
            temp["categoryLink"] = category.categoryLink
            temp["discription"] = category.discription
            categoryArr.append(temp)
        return HttpResponse(json.dumps({'data': categoryArr}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def reviewFetcher(request):
    if request.method == 'GET':
        url = "https://www.google.com/maps/preview/review/listentitiesreviews?pb=!1m2!1y4133920741275602995!2y10276051086807358622!2m1!2i10!3e1!4m6!3b1!4b1!5b1!6b1!7b1!20b1!5m2!1s4GgJZOaEIPKYseMP4oCl8A8!7e81"
        payload={}
        headers = {
            'authority': 'www.google.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,gu;q=0.8',
            'referer': 'https://www.google.com/',
            'sec-ch-ua-model': '',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
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
            temp = {}
            temp["name"] = i[0][1]
            temp["image"] = i[0][2].replace("br100","br0")
            temp["time"] = i[1]
            temp["review"] = i[3]
            temp["rating"] = i[4]
            data.append(temp)
        return HttpResponse(json.dumps({'data': data}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def clientList(request):
    if request.method == 'GET':
        clientList = Clients.objects.all()
        clientArr = []
        for client in clientList:
            clientArr.append([client.name,"/media/images/logo/"+str(client.image.url).split("/")[-1],client.link])
        return HttpResponse(json.dumps({'data': clientArr}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def youtubeVideoList(request):
    if request.method == 'GET':
        videoList = YoutubeVideo.objects.filter(isUploaded=True).all()
        videoArr = []
        for video in videoList:
            videoArr.append([video.title,"https://www.youtube.com/embed/"+video.videoId+"?autoplay=0&mute=1&loop=1&showinfo=0&controls=0"])
        return HttpResponse(json.dumps({'data': videoArr}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def quoteList(request):
    if request.method == 'GET':
        categoryLink = request.GET.get('category')
        print(categoryLink)
        category = Category.objects.filter(categoryLink=categoryLink).first()
        quotes = Quote.objects.filter(category=category)
        quotesCount = quotes.count()
        if quotesCount > 0:
            quoteList = quotes.all()
            quoteArr = []
            for quote in quoteList:
                quoteArr.append(quote.quote)
            return HttpResponse(json.dumps({'data': quoteArr}), content_type='application/json')
        else:
            quotes = Quote.objects.filter(isMHE=True).all()
            quoteArr = []
            for quote in quotes:
                quoteArr.append(quote.quote)
            return HttpResponse(json.dumps({'data': quoteArr}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def contactus(request):
    if request.method == 'POST':
        name = request.POST.get('name') 
        email = request.POST.get('email') 
        phoneNo = request.POST.get('phoneNo') 
        country = request.POST.get('country') 
        companyName = request.POST.get('companyName') 
        query = request.POST.get('query') 
        address = request.POST.get('address') 
        isSuscribed = request.POST.get('isSuscribed') 
        print(name,email,phoneNo,country,companyName,query,address,isSuscribed)
        contactus = contactUs()
        contactus.name = name
        contactus.email = email
        contactus.phoneNo = phoneNo
        contactus.country = country
        contactus.companyName = companyName
        contactus.query = query
        contactus.address = address
        if isSuscribed == "on":
            isSuscribed = True
        else:
            isSuscribed = False
        contactus.isSuscribed = isSuscribed
        contactus.save()
        return HttpResponse(json.dumps({'data': 'success'}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def searchDatabase(request):
    if request.method == 'GET':
        searchQuery = request.GET.get('searchQuery')
        searchQuery = searchQuery.lower()
        result = {"products":[],"categories":[]}
        # search searchQuery in Product and append in result
        productsName = Product.objects.filter(productName__contains=searchQuery).all()
        productsDiscription = Product.objects.filter(description__contains=searchQuery).all()
        for product in productsName:
            result["products"].append([product.productName,product.category.categoryName,(product.images.url).split("/")[-1],product.productLink])
        for product in productsDiscription:
            result["products"].append([product.productName,product.category.categoryLink,(product.images.url).split("/")[-1],product.productLink])
        result = {"products":result["products"][:5],"categories":[]}
        categoriesName = Category.objects.filter(categoryName__contains=searchQuery).all()
        categoriesDiscription = Category.objects.filter(discription__contains=searchQuery).all()
        for category in categoriesName:
            result["categories"].append([category.categoryName,category.categoryLink])
        for category in categoriesDiscription:
            result["categories"].append([category.categoryName,category.categoryLink])
        result = {"products":result["products"],"categories":result["categories"][:5]}
        return HttpResponse(json.dumps({'data': result}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')

@csrf_exempt
def likeProduct(request):
    if request.method == 'GET':
        productName = request.GET.get('title')
        product = Product.objects.filter(productName = productName).first()
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
                    return HttpResponse(json.dumps({'msg': "success","data":likes}), content_type='application/json')
                else:
                    product.likes.add(Ip.objects.filter(ip=ip).first())
                    product.save()
                    likes = product.total_likes()
                    return HttpResponse(json.dumps({'msg': "success","data":likes}), content_type='application/json')
                return HttpResponse(json.dumps({'msg': "success"}), content_type='application/json')
            else:
                return HttpResponse(json.dumps({'error': "failed"}), content_type='application/json')
        else:
            return HttpResponse(json.dumps({'error': "failed"}), content_type='application/json')
    return HttpResponse(json.dumps({'error': 'You were not supposed be here.'}), content_type='application/json')


@csrf_exempt
def dataAdder(request):
    data = {
        "Aerial Work Platform": [
            {
                "link": "https://www.kijeka.com/product/aluminium-aerial-work-platform-double-mast/",
                "name": "Aluminium Aerial Work Platform (Double Mast)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Aerial Work Platform is a cost-effective lift option. These versatile machines combine tight access maneuverability with ample space for two workers and their tools on\u00a0a large platform</li>\n<li>Aerial Work Platform offer exceptional stability with a patented aluminum mast system, heavy-duty lifting chains and welded steel base that stands up to rough jobsite conditions. Bottom line, they\u2019re the ideal choice for big jobs in small spaces.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Features:</strong></p>\n<ul>\n<li>Aluminium mast structure, lifting smooth, lightweight mobile</li>\n<li>Platform can be controlled up and down, with emergency button</li>\n<li>Leakage protection, thermal protection, emergency travel protection</li>\n<li>Power failure self-locking, emergency decline, fuel tank anti-cracking device</li>\n</ul>\n<ul>\n<li>Quick to set-up and simple to operate</li>\n<li>Non-marking swivel-lock casters for 360\u02da rotation in small spaces</li>\n<li>Convenient handle for easy\u00a0steering and maneuverability, even though\u00a0standard doorways</li>\n<li>Easy transport with\u00a0 multi-directional forklift pockets,\u00a0outrigger storage sockets\u00a0and sturdy tie-down attachments point</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td colspan=\"6\">\u00a0<strong>Aluminium Aerial Work Platform (Double Mast)</strong></td>\n</tr>\n<tr>\n<td colspan=\"2\">Safe working load</td>\n<td>200KG</td>\n<td>200KG</td>\n<td>200KG</td>\n<td>200KG</td>\n<td>200KG</td>\n<td>150KG</td>\n</tr>\n<tr>\n<td colspan=\"2\">Allowable number of people</td>\n<td>1</td>\n<td>1</td>\n<td>1</td>\n<td>1</td>\n<td>1</td>\n<td>1</td>\n</tr>\n<tr>\n<td colspan=\"2\">The maximum working height</td>\n<td>8.00M</td>\n<td>10.00M</td>\n<td>11.00M</td>\n<td>12.00M</td>\n<td>14.00M</td>\n<td>16.00M</td>\n</tr>\n<tr>\n<td colspan=\"2\">The maximum platform height</td>\n<td>6.00M</td>\n<td>8.00M</td>\n<td>9.00M</td>\n<td>10.00M</td>\n<td>12.00M</td>\n<td>14.00M</td>\n</tr>\n<tr>\n<td colspan=\"2\">Machine length</td>\n<td>1.54M</td>\n<td>1.54M</td>\n<td>1.54M</td>\n<td>1.76M</td>\n<td>1.76M</td>\n<td>1.90M</td>\n</tr>\n<tr>\n<td colspan=\"2\">Machine width</td>\n<td>1.00M</td>\n<td>1.00M</td>\n<td>1.00M</td>\n<td>1.00M</td>\n<td>1.00M</td>\n<td>1.16M</td>\n</tr>\n<tr>\n<td colspan=\"2\">Machine height</td>\n<td>2.00M</td>\n<td>2.00M</td>\n<td>2.00M</td>\n<td>2.00M</td>\n<td>2.00M</td>\n<td>2.35M</td>\n</tr>\n<tr>\n<td colspan=\"2\">Rise Time (S)</td>\n<td>55 S</td>\n<td>75 S</td>\n<td>80 S</td>\n<td>88 S</td>\n<td>100 S</td>\n<td>112 S</td>\n</tr>\n<tr>\n<td colspan=\"2\">Work platform size</td>\n<td>1.30 * 0.62M</td>\n<td>1.30 * 0.62M</td>\n<td>1.30 * 0.62M</td>\n<td>1.52 * 0.62M</td>\n<td>1.52 * 0.62M</td>\n<td>1.52 * 0.62M</td>\n</tr>\n<tr>\n<td colspan=\"2\">Outrigger Footprint</td>\n<td>1.77 * 1.82M</td>\n<td>1.77 * 1.82M</td>\n<td>1.77 * 1.82M</td>\n<td>2.1 * 2.00M</td>\n<td>2.1 * 2.00M</td>\n<td>2.36 * 2.33M</td>\n</tr>\n<tr>\n<td colspan=\"2\">Minimum ground clearance</td>\n<td>0.05M</td>\n<td>0.05M</td>\n<td>0.05M</td>\n<td>0.05M</td>\n<td>0.05M</td>\n<td>0.05M</td>\n</tr>\n<tr>\n<td colspan=\"2\">Lifting motor (\u00a0AC\u00a0)</td>\n<td>1.1KW</td>\n<td>1.1KW</td>\n<td>1.1KW</td>\n<td>1.1KW</td>\n<td>1.1KW</td>\n<td>1.5KW</td>\n</tr>\n<tr>\n<td colspan=\"2\">Machine weight\u00a0(AC)</td>\n<td>630KG</td>\n<td>680KG</td>\n<td>730KG</td>\n<td>800KG</td>\n<td>830KG</td>\n<td>904KG</td>\n</tr>\n<tr>\n<td rowspan=\"3\">Optional</td>\n<td>Power storage</td>\n<td>24V / 100Ah</td>\n<td>24V / 100Ah</td>\n<td>24V / 100Ah</td>\n<td>24V / 100Ah</td>\n<td>24V / 100Ah</td>\n<td>24V / 100Ah</td>\n</tr>\n<tr>\n<td>Hoisting motor (DC)</td>\n<td>0.80KW</td>\n<td>0.80KW</td>\n<td>0.80KW</td>\n<td>0.80KW</td>\n<td>1.5KW</td>\n<td>1.5KW</td>\n</tr>\n<tr>\n<td>charger</td>\n<td>24V / 12A</td>\n<td>24V / 12A</td>\n<td>24V / 12A</td>\n<td>24V / 12A</td>\n<td>24V / 12A</td>\n<td>24V / 12A</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Aluminium-Aerial-Work-Platform.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Aluminium-Aerial-Work-Platform.png 310w, https://www.kijeka.com/wp-content/uploads/2017/11/Aluminium-Aerial-Work-Platform-119x300.png 119w, https://www.kijeka.com/wp-content/uploads/2017/11/Aluminium-Aerial-Work-Platform-270x679.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/aluminium-aerial-work-platform-single-mast/",
                "name": "Aluminium Aerial Work Platform (Single Mast)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>An aerial work platform is a device used to provide temporary access for people or equipment to inaccessible areas, usually at height. They are generally used for temporary, flexible access purposes such as maintenance and construction work or by firefighters for emergency access.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Uses:</strong></p>\n<ul>\n<li>Indoor and Outdoor Lighting Maintenance, Renovation Work, Painting Applications, Industrial, and many more uses.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Features:</strong></p>\n<ul>\n<li>Aluminium mast structure, lifting smooth, lightweight mobile</li>\n<li>Platform can be controlled up and down, with emergency button</li>\n<li>Leakage protection, thermal protection, emergency travel protection</li>\n<li>Power failure self-locking, emergency decline, fuel tank anti-cracking device</li>\n</ul>\n<ul>\n<li>Quick to set-up and simple to operate</li>\n<li>Non-marking swivel-lock casters for 360\u02da rotation in small spaces</li>\n<li>Convenient handle for easy\u00a0steering and maneuverability, even though\u00a0standard doorways</li>\n<li>Easy transport with\u00a0 multi-directional forklift pockets,\u00a0outrigger storage sockets\u00a0and sturdy tie-down attachments point</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"208\">\n<p style=\"text-align: center;\"><strong>Product number</strong></p>\n</td>\n<td colspan=\"4\" width=\"300\">\u00a0<strong>Aluminium Aerial Work Platform- Single Mast</strong></td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"208\">Safe working load</td>\n<td width=\"57\">130KG</td>\n<td>130KG</td>\n<td>130KG</td>\n<td>130KG</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"208\">Allowable number of people</td>\n<td width=\"57\">1</td>\n<td>1</td>\n<td>1</td>\n<td>1</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"208\">The maximum working height</td>\n<td width=\"57\">8.00M</td>\n<td>10.00M</td>\n<td>11.00M</td>\n<td>12.00M</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"208\">The maximum platform height</td>\n<td width=\"57\">6.00M</td>\n<td>8.00M</td>\n<td>9.00M</td>\n<td>10.00M</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"208\">Machine length C</td>\n<td width=\"57\">1.34M</td>\n<td>1.34M</td>\n<td>1.45M</td>\n<td>1.45M</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"208\">Machine width W</td>\n<td width=\"57\">0.85M</td>\n<td>0.85M</td>\n<td>0.85M</td>\n<td>0.85M</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"208\">Machine height H0</td>\n<td width=\"57\">2.00M</td>\n<td>2.00M</td>\n<td>2.00M</td>\n<td>2.00M</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"208\">Work platform size</td>\n<td width=\"57\">0.60 * 0.55M</td>\n<td>0.60 * 0.55M</td>\n<td>0.60 * 0.55M</td>\n<td>0.60 * 0.55M</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"208\">Rise Time</td>\n<td width=\"57\">55S</td>\n<td>75S</td>\n<td>80S</td>\n<td>88S</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"208\">Outrigger Footprint</td>\n<td width=\"57\">1.7 * 1.67M</td>\n<td>1.7 * 1.67M</td>\n<td>1.93 * 1.77M</td>\n<td>1.93 * 1.77M</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"208\">Minimum ground clearance</td>\n<td width=\"57\">0.05M</td>\n<td>0.05M</td>\n<td>0.05M</td>\n<td>0.05M</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"208\">Lifting motor (AC)</td>\n<td width=\"57\">0.75KW</td>\n<td>0.75KW</td>\n<td>0.75KW</td>\n<td>1.1KW</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"208\">Machine weight (AC)</td>\n<td width=\"57\">325KG</td>\n<td>378KG</td>\n<td>400KG</td>\n<td>430KG</td>\n</tr>\n<tr>\n<td rowspan=\"3\" width=\"64\">Optional</td>\n<td width=\"143\">Battery</td>\n<td width=\"57\">24V / 80Ah</td>\n<td>24V / 80Ah</td>\n<td>24V / 80Ah</td>\n<td>24V / 80Ah</td>\n</tr>\n<tr>\n<td width=\"143\">Hoisting motor (DC)</td>\n<td width=\"57\">0.80KW</td>\n<td>0.80KW</td>\n<td>0.80KW</td>\n<td>0.80KW</td>\n</tr>\n<tr>\n<td width=\"143\">charger</td>\n<td width=\"57\">24V / 12A</td>\n<td>24V / 12A</td>\n<td>24V / 12A</td>\n<td>24V / 12A</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Aluminium-Aerial-Work-Platform-Double-Mast.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Aluminium-Aerial-Work-Platform-Double-Mast.png 493w, https://www.kijeka.com/wp-content/uploads/2017/11/Aluminium-Aerial-Work-Platform-Double-Mast-267x300.png 267w, https://www.kijeka.com/wp-content/uploads/2017/11/Aluminium-Aerial-Work-Platform-Double-Mast-270x303.png 270w"
                    ]
                ]
            }
        ],
        "Aluminium Ladders": [
            {
                "link": "https://www.kijeka.com/product/aluminum-mobile-staircase-ladder/",
                "name": "Aluminum Mobile Staircase Ladder",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Aluminum Movable Staircase Ladder manufactured from C Section of 67x31x3mm &amp; 8 inch Aluminum Chequered Plates Steps with Large 24\u2033 x24\u2033</li>\n<li>Aluminum Non Skid Platform for standing, 2ft Guard Rail on top,</li>\n<li>Staircase Ladder Base On 4 nos wheels (2 nos. Fixed and 2nos Swivel with brakes), MS angle Cross Supports and MS heavy base Bottom</li>\n<li>Aluminum Conforming to HE -30 Grade T -6 Temper as per IS 733<br/>\n<table width=\"192\">\n<tbody>\n<tr>\n<td colspan=\"2\" style=\"text-align: center;\" width=\"250\"><strong>Available Sizes</strong></td>\n</tr>\n<tr>\n<td width=\"130\"><strong>Height Up to Platform\u00a0</strong></td>\n<td width=\"70\"><b>Total Height\u00a0</b></td>\n</tr>\n<tr>\n<td width=\"130\">3 feet</td>\n<td width=\"70\">5 feet</td>\n</tr>\n<tr>\n<td width=\"130\">4 feet</td>\n<td width=\"70\">6 feet</td>\n</tr>\n<tr>\n<td width=\"130\">5 feet</td>\n<td width=\"70\">8 feet</td>\n</tr>\n<tr>\n<td width=\"130\">8 feet</td>\n<td width=\"70\">10 feet</td>\n</tr>\n<tr>\n<td width=\"130\">10 feet</td>\n<td width=\"70\">12 feet</td>\n</tr>\n<tr>\n<td width=\"130\">12 feet</td>\n<td width=\"70\">14 feet</td>\n</tr>\n</tbody>\n</table>\n<p>\u00a0</p></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/1-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/1-scaled.jpg 2560w, https://www.kijeka.com/wp-content/uploads/2021/04/1-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/1-1024x1024.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2021/04/1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/1-768x768.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/1-1536x1536.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2021/04/1-2048x2048.jpg 2048w, https://www.kijeka.com/wp-content/uploads/2021/04/1-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/1-270x270.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/1-370x370.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/1-1170x1170.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2021/04/1-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-2-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-2-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-2-270x270.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-2-370x370.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-2-170x170.jpg 170w, https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-2.jpg 600w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-270x270.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-370x370.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder-170x170.jpg 170w, https://www.kijeka.com/wp-content/uploads/2021/04/Kijeka_Ladder.jpg 600w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/aluminum-square-tower-ladders/",
                "name": "Aluminum Square Tower  Ladders",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Manufactured from High Tensile Aluminum Alloys</li>\n<li>Section Size Width: Aluminum \u201cC\u201d Section(HE-30 Grade) Size: 66.6mm x 31.25mm</li>\n<li>Material Standard: Confirm HE-30 Grade T-6 Temper, IS 733-1982</li>\n<li>Ladder Base Material MOC : Heavy Duty MS Channel &amp; MS Angles</li>\n<li>Step Details: Aluminum 25.4 mm Round Corrugated Tubes</li>\n<li>Distance Between Two Steps-10/ 12\u201d Centre to Centre</li>\n<li>Locking Facility: Pendulum Lock, Winch Gear Equipped with Dual Locking Facilities</li>\n<li>Operating Facility: 01 No. Winch Gear Machine with required Wire Rope &amp; Pulleys for Extending &amp; Closing the Ladder</li>\n<li>Size Of Top Platform: 18\u201d X 21\u201d (3-feet Below from Top)</li>\n<li>Wheel Option: Available with Solid Hard Polymer, Rubber Or Pneumatic Rubber Wheels</li>\n<li><strong>Having 4-jacks for braking as well as levelling purpose.</strong></li>\n<li>Other Features: Safety Stoppers, Safety Belt, Safety Helmet,</li>\n<li><strong>Available with : 2- Section &amp; 3- Section </strong></li>\n</ul>\n<p><strong>\u00a0</strong></p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"208\"><strong>Available Sizes\u00a0</strong><strong>In\u00a0</strong><strong style=\"font-family: inherit; font-size: inherit;\">2- Section</strong></td>\n</tr>\n<tr>\n<td width=\"106\"><strong>Closed Height</strong></td>\n<td width=\"103\"><strong>Extended\u00a0</strong><strong>Height</strong></td>\n</tr>\n<tr>\n<td width=\"102\">8 ft.</td>\n<td width=\"103\">14 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">10 ft.</td>\n<td width=\"103\">17 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">12 ft.</td>\n<td width=\"103\">21 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">14 ft.</td>\n<td width=\"103\">25 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">16 ft.</td>\n<td width=\"103\">29 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">18 ft.</td>\n<td width=\"103\">32 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">20 ft.</td>\n<td width=\"103\">35 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">24 ft.</td>\n<td width=\"103\">43 ft.</td>\n</tr>\n</tbody>\n</table>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"208\"><strong>Available Sizes\u00a0</strong><strong>In\u00a0</strong><strong>3- Section</strong></td>\n</tr>\n<tr>\n<td width=\"106\"><strong>Closed\u00a0</strong><strong>Height</strong></td>\n<td width=\"102\"><strong>Extended\u00a0</strong><strong>Height</strong></td>\n</tr>\n<tr>\n<td width=\"106\">12 ft.</td>\n<td width=\"102\">30 ft.</td>\n</tr>\n<tr>\n<td width=\"106\">14 ft.</td>\n<td width=\"102\">36 ft.</td>\n</tr>\n<tr>\n<td width=\"106\">16 ft.</td>\n<td width=\"102\">40 ft.</td>\n</tr>\n<tr>\n<td width=\"106\">20 ft.</td>\n<td width=\"102\">50 ft.</td>\n</tr>\n<tr>\n<td width=\"106\">24 ft.</td>\n<td width=\"102\">60 ft.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Aluminum-Square-Tower-Ladders-copy-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Aluminum-Square-Tower-Ladders-copy-scaled.jpg 1810w, https://www.kijeka.com/wp-content/uploads/2021/04/Aluminum-Square-Tower-Ladders-copy-212x300.jpg 212w, https://www.kijeka.com/wp-content/uploads/2021/04/Aluminum-Square-Tower-Ladders-copy-724x1024.jpg 724w, https://www.kijeka.com/wp-content/uploads/2021/04/Aluminum-Square-Tower-Ladders-copy-768x1086.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/Aluminum-Square-Tower-Ladders-copy-1086x1536.jpg 1086w, https://www.kijeka.com/wp-content/uploads/2021/04/Aluminum-Square-Tower-Ladders-copy-1448x2048.jpg 1448w, https://www.kijeka.com/wp-content/uploads/2021/04/Aluminum-Square-Tower-Ladders-copy-64x90.jpg 64w, https://www.kijeka.com/wp-content/uploads/2021/04/Aluminum-Square-Tower-Ladders-copy-247x350.jpg 247w, https://www.kijeka.com/wp-content/uploads/2021/04/Aluminum-Square-Tower-Ladders-copy-339x480.jpg 339w, https://www.kijeka.com/wp-content/uploads/2021/04/Aluminum-Square-Tower-Ladders-copy-1170x1655.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2021/04/Aluminum-Square-Tower-Ladders-copy-270x382.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/combination-ladders/",
                "name": "Combination Ladders",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Manufactured from high tensile aluminum alloy ,this ladder is compact, light in weight yet sturdy, foldable and suitable where no wall support is available .</li>\n<li><strong>Combines two functions into one ladder.</strong></li>\n<li><strong>Ladder converts quickly and safely from a self Supporting ladder\u00a0Into a Wall supporting ladder</strong></li>\n<li>Side Section : 67 mm Aluminum \u2018C\u2019 section(HE-30 Grade)</li>\n<li>Step Details:63mm Aluminum Flat Step</li>\n<li>63mm fully serrated Steps ensures anti-slip surface and firm grip place at 12\u2033 Inches c/c</li>\n<li>Others Specification: Rubber shoes, M.S hinges etc.</li>\n</ul>\n<table style=\"height: 347px;\" width=\"253\">\n<tbody>\n<tr>\n<td colspan=\"2\" style=\"text-align: center;\" width=\"205\"><strong>\u00a0Available Size\u00a0</strong></td>\n</tr>\n<tr>\n<td width=\"110\">\u00a0Height In <strong>\u201cA\u201d\u00a0</strong> \u00a0Position</td>\n<td width=\"103\">\u00a0Height In <strong>\u201cH\u201d</strong>\u00a0 \u00a0Position</td>\n</tr>\n<tr>\n<td width=\"102\">5 ft.</td>\n<td width=\"103\">9 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">6 ft.</td>\n<td width=\"103\">11 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">7 ft.</td>\n<td width=\"103\">13 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">8 ft.</td>\n<td width=\"103\">15 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">9 ft.</td>\n<td width=\"103\">17 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">10 ft.</td>\n<td width=\"103\">19 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">20 ft.</td>\n<td width=\"103\">35 ft.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/combination-Ladder-copy-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/combination-Ladder-copy-scaled.jpg 1605w, https://www.kijeka.com/wp-content/uploads/2021/04/combination-Ladder-copy-188x300.jpg 188w, https://www.kijeka.com/wp-content/uploads/2021/04/combination-Ladder-copy-642x1024.jpg 642w, https://www.kijeka.com/wp-content/uploads/2021/04/combination-Ladder-copy-768x1225.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/combination-Ladder-copy-963x1536.jpg 963w, https://www.kijeka.com/wp-content/uploads/2021/04/combination-Ladder-copy-1284x2048.jpg 1284w, https://www.kijeka.com/wp-content/uploads/2021/04/combination-Ladder-copy-56x90.jpg 56w, https://www.kijeka.com/wp-content/uploads/2021/04/combination-Ladder-copy-219x350.jpg 219w, https://www.kijeka.com/wp-content/uploads/2021/04/combination-Ladder-copy-301x480.jpg 301w, https://www.kijeka.com/wp-content/uploads/2021/04/combination-Ladder-copy-1170x1866.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2021/04/combination-Ladder-copy-270x431.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/magic-pole-ladder/",
                "name": "Magic Pole Ladders",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Magic Pole Ladder Wall Supporting Ladders Aluminum Single Ladder Manufactured from C Section of 67x31x3mm</li>\n<li>Necessary lock to keep ladder locked in closed and open position</li>\n<li>Material Standard: Confirm HE-30 Grade T-6 Temper, IS 733-1982</li>\n<li>Step Details: 63mm <strong>Fully Serrated Steps ensure Antislip Surface &amp; firm grip placed at 10\u2033/12\u2033</strong></li>\n<li>Solid Robber Shoes At Bottom to avoid surface scratching</li>\n<li>Available with <strong>\u201cJ\u201d Or \u201cL\u201d</strong> Type Hook at the Top of Ladder</li>\n<li><strong>Available Height:</strong> 6,8,10,12,14 feets</li>\n</ul>\n</div>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Magic-Pole-Ladders-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Magic-Pole-Ladders-scaled.jpg 1322w, https://www.kijeka.com/wp-content/uploads/2021/04/Magic-Pole-Ladders-155x300.jpg 155w, https://www.kijeka.com/wp-content/uploads/2021/04/Magic-Pole-Ladders-529x1024.jpg 529w, https://www.kijeka.com/wp-content/uploads/2021/04/Magic-Pole-Ladders-768x1487.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/Magic-Pole-Ladders-793x1536.jpg 793w, https://www.kijeka.com/wp-content/uploads/2021/04/Magic-Pole-Ladders-1058x2048.jpg 1058w, https://www.kijeka.com/wp-content/uploads/2021/04/Magic-Pole-Ladders-46x90.jpg 46w, https://www.kijeka.com/wp-content/uploads/2021/04/Magic-Pole-Ladders-181x350.jpg 181w, https://www.kijeka.com/wp-content/uploads/2021/04/Magic-Pole-Ladders-248x480.jpg 248w, https://www.kijeka.com/wp-content/uploads/2021/04/Magic-Pole-Ladders-1170x2265.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2021/04/Magic-Pole-Ladders-270x523.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/polymer-wheeled-extension-ladders/",
                "name": "Polymer Wheeled Extension Ladders",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Ideal for Electrical works, Domestic purpose, or any Industrial job at a height.</li>\n<li>Manufactured from High Tensile Aluminium Alloys.</li>\n<li>An economical variety in aluminium tower, extending section adjusts Intermediately</li>\n<li>Elegant, sturdy, light in weight, extremely useful where no wall Support is available to ladders</li>\n<li>Equipped with Manila Rope, Pulley, Safety locks, Safety Ring, Solid Polymer wheel for Better movement</li>\n<li>Having Solid rubber shoe to avoid surface scratching.</li>\n<li>Section : Aluminium \u2018C\u2019 section(HE-30 Grade) Size: 66.6mm x 31.25mm</li>\n</ul>\n<ul>\n<li><strong>Ladder Height: As per Below Table </strong></li>\n<li>Step Details: Aluminium 25.5mm Round corrugated tube</li>\n<li>Locking Facility : Aluminium Die Casted catcher (Lockable at every 12inches)</li>\n<li>Operating Facility : Nylon rope &amp; pulleys for extending &amp; closing the ladder</li>\n<li>Top Platform Size: 8\u2033 x 11\u2033(3ft. Below from top)</li>\n<li>Distance between two steps: 12\u2033 Inches c/c</li>\n<li>Confirms to: HE-30grade T-6 Temper, IS : 733 \u2013 1982</li>\n</ul>\n<ul>\n<li>Other Technical Details: Safety Ring at top, Rubber shoes, M.S hinges etc.</li>\n</ul>\n<ul>\n<li><strong>Available with : 2- Section<br/>\n</strong></li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"250\"><strong>Available Sizes\u00a0</strong><strong>In\u00a0</strong><strong>2- Section</strong></td>\n</tr>\n<tr>\n<td width=\"130\"><strong>Closed Height</strong></td>\n<td width=\"70\"><strong>Extended\u00a0</strong><strong>Height</strong></td>\n</tr>\n<tr>\n<td width=\"130\">8 ft.</td>\n<td width=\"70\">14 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">10 ft.</td>\n<td width=\"70\">17 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">12 ft.</td>\n<td width=\"70\">21 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">14 ft.</td>\n<td width=\"70\">25 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">16 ft.</td>\n<td width=\"70\">29 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">18 ft.</td>\n<td width=\"70\">32 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">20 ft.</td>\n<td width=\"70\">35 ft.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Polymer-Wheeled-Extention-Ladders-1.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Polymer-Wheeled-Extention-Ladders-1.jpg 756w, https://www.kijeka.com/wp-content/uploads/2017/12/Polymer-Wheeled-Extention-Ladders-1-125x300.jpg 125w, https://www.kijeka.com/wp-content/uploads/2017/12/Polymer-Wheeled-Extention-Ladders-1-426x1024.jpg 426w, https://www.kijeka.com/wp-content/uploads/2017/12/Polymer-Wheeled-Extention-Ladders-1-37x90.jpg 37w, https://www.kijeka.com/wp-content/uploads/2017/12/Polymer-Wheeled-Extention-Ladders-1-145x350.jpg 145w, https://www.kijeka.com/wp-content/uploads/2017/12/Polymer-Wheeled-Extention-Ladders-1-199x480.jpg 199w, https://www.kijeka.com/wp-content/uploads/2017/12/Polymer-Wheeled-Extention-Ladders-1-270x650.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/recess-platform-ladder/",
                "name": "Recess Platform Ladder",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Manufactured from high tensile aluminum alloy</li>\n<li>Compact, light\u00a0in weight yet sturdy, foldable and suitable where no wall support is available.</li>\n<li><strong>Aluminum Slip resistant platform of 13\u2033x 16\u2033 for Convenient Working.</strong></li>\n<li>Section Size Width: Aluminum \u201cC\u201d Section(HE-30 Grade) Size: 66.6mm x 31.25mm</li>\n<li>Material Standard: Confirm HE-30 Grade T-6 Temper, IS 733-1982</li>\n<li>Step Details: Anti Slip 63mm Aluminum Flat Steps</li>\n<li>Distance Between Two Steps-10\u2033/ 12\u201d Centre to Centre</li>\n<li>Folding Sway Protectors which Prevents Sway of the back section of Ladder While Folded</li>\n<li>Solid Robber Shoes At Bottom to avoid surface scratching</li>\n</ul>\n<table style=\"height: 270px;\" width=\"192\">\n<tbody>\n<tr>\n<td colspan=\"2\" style=\"text-align: center;\" width=\"250\"><strong>Available Sizes</strong></td>\n</tr>\n<tr>\n<td width=\"130\"><strong>Height Up to Platform\u00a0</strong></td>\n<td width=\"70\"><b>Total Height\u00a0</b></td>\n</tr>\n<tr>\n<td width=\"130\">5 feet</td>\n<td width=\"70\">8 feet</td>\n</tr>\n<tr>\n<td width=\"130\">7 feet</td>\n<td width=\"70\">10 feet</td>\n</tr>\n<tr>\n<td width=\"130\">9 feet</td>\n<td width=\"70\">12 feet</td>\n</tr>\n<tr>\n<td width=\"130\">11 feet</td>\n<td width=\"70\">14 feet</td>\n</tr>\n<tr>\n<td width=\"130\">13 feet</td>\n<td width=\"70\">16 feet</td>\n</tr>\n<tr>\n<td width=\"130\">15 feet</td>\n<td width=\"70\">18 feet</td>\n</tr>\n<tr>\n<td width=\"130\"></td>\n<td width=\"70\"></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1378-copy-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1378-copy-scaled.jpg 1218w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1378-copy-143x300.jpg 143w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1378-copy-487x1024.jpg 487w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1378-copy-768x1614.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1378-copy-731x1536.jpg 731w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1378-copy-974x2048.jpg 974w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1378-copy-43x90.jpg 43w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1378-copy-166x350.jpg 166w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1378-copy-228x480.jpg 228w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1378-copy-1170x2460.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1378-copy-270x568.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/road-star-tower-ladders/",
                "name": "Road Star Tower Ladders",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Ideal for Electrical works, Domestic purpose, or any Industrial job at a height.</li>\n<li>Manufactured from High Tensile Aluminum Alloys.</li>\n<li>An economical variety in aluminum tower, extending section adjusts Intermediately</li>\n<li>Reinforced with M.S. railing to enable safe and easy climbing.</li>\n<li>Elegant, sturdy, light in weight, extremely useful where no wall Support is available to ladders</li>\n<li>Having Solid rubber shoe to avoid surface scratching.</li>\n<li>Section Size Width: Aluminum \u201cC\u201d Section(HE-30 Grade) Size: 66.6mm x 31.25mm</li>\n<li>Material Standard: Confirm HE-30 Grade T-6 Temper, IS 733-1982</li>\n<li>Step Details: Aluminum 25.4 mm Round Corrugated Tubes</li>\n<li>Distance Between Two Steps- 12\u201d Centre to Centre</li>\n<li>Locking Facility: Pendulum Lock, Winch Gear Equipped with Dual Locking Facilities</li>\n<li>Operating Facility: 01 No. Winch Gear Machine with required Wire Rope &amp; Pulleys for Extending &amp; Closing the Ladder</li>\n<li>Size Of Top Platform: 18\u201d X 21\u201d (3-feet Below from Top)</li>\n<li>Wheel : M.S. fabricated spoke type wheels mounted on axle, with leaf spring,</li>\n<li>Other Features: Manila Rope, Pulley, Safety locks, Safety Ring, with rubber rib fitted with M.S. wheel</li>\n</ul>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"250\"><strong>Available Sizes\u00a0</strong><strong>In\u00a0</strong><strong style=\"font-family: inherit; font-size: inherit;\">2- Section</strong></td>\n</tr>\n<tr>\n<td width=\"130\"><strong>Closed Height</strong></td>\n<td width=\"70\"><strong>Extended\u00a0</strong><strong>Height</strong></td>\n</tr>\n<tr>\n<td width=\"130\">8 ft.</td>\n<td width=\"70\">14 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">10 ft.</td>\n<td width=\"70\">17 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">12 ft.</td>\n<td width=\"70\">21 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">14 ft.</td>\n<td width=\"70\">25 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">16 ft.</td>\n<td width=\"70\">29 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">18 ft.</td>\n<td width=\"70\">32 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">20 ft.</td>\n<td width=\"70\">35 ft.</td>\n</tr>\n</tbody>\n</table>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"250\"><strong>Available Sizes\u00a0</strong><strong>In\u00a0</strong><strong style=\"font-family: inherit; font-size: inherit;\">3- Section</strong></td>\n</tr>\n<tr>\n<td width=\"130\"><strong>Closed Height</strong></td>\n<td width=\"70\"><strong>Extended\u00a0</strong><strong>Height</strong></td>\n</tr>\n<tr>\n<td width=\"130\">10 ft.</td>\n<td width=\"70\">24 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">12 ft.</td>\n<td width=\"70\">30 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">14 ft.</td>\n<td width=\"70\">36 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">16 ft.</td>\n<td width=\"70\">40 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">18 ft.</td>\n<td width=\"70\">45 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">20 ft.</td>\n<td width=\"70\">50 ft.</td>\n</tr>\n<tr>\n<td width=\"130\">24 ft.</td>\n<td width=\"70\">60 ft.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Road-Star-Tower-Ladders.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Road-Star-Tower-Ladders.png 197w, https://www.kijeka.com/wp-content/uploads/2017/10/Road-Star-Tower-Ladders-139x300.png 139w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/self-supported-extension-ladder_mobile-folding/",
                "name": "Self- Supported Extension Ladder (Mobile Folding)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Ideal for Electrical works, Domestic purpose, or any Industrial job at a height.</li>\n<li>Manufactured from High Tensile Aluminum Alloys.</li>\n<li>An economical variety in aluminum tower, extending section adjusts Intermediately</li>\n<li>Section : Aluminum \u2018C\u2019 section(HE-30 Grade) Size: 66.6mm x 31.25mm</li>\n<li><b>Step Details: Aluminum 25.5 mm Round corrugated steps ensure anti Slip Surface</b></li>\n<li><b>Locking Facility : Aluminum Die Casted catcher (Lockable at every 12 Inches)</b></li>\n<li><b>Wheels &amp; Jacks:\u00a0 Swivel Type 04 Nos. Wheels for Easy Maneuverability &amp; 04 Nos Turn Jacks for Stability\u00a0</b></li>\n<li>Operating Facility : Nylon rope &amp; pulleys for extending &amp; closing the ladder</li>\n<li><strong>Top Platform Size: 8\u2033 x 16\u2033(3ft. Below from top)</strong></li>\n<li><strong>Distance between two steps: 12\u2033 Inches c/c</strong></li>\n<li>Other Technical Details: Safety Ring at top, Rubber shoes, M.S hinges etc.</li>\n<li><strong>Available with : 2- Section</strong></li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"205\"><strong>Available Sizes\u00a0</strong><strong>In\u00a0</strong><strong>2-Section </strong></td>\n</tr>\n<tr>\n<td width=\"110\"><strong>Closed Height</strong></td>\n<td width=\"103\"><strong>Extended\u00a0</strong><strong>Height</strong></td>\n</tr>\n<tr>\n<td width=\"102\">8 ft.</td>\n<td width=\"103\">14 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">10 ft.</td>\n<td width=\"103\">17 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">12 ft.</td>\n<td width=\"103\">21 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">14 ft.</td>\n<td width=\"103\">25 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">16 ft.</td>\n<td width=\"103\">29 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">18 ft.</td>\n<td width=\"103\">32 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">20 ft.</td>\n<td width=\"103\">35 ft.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/12-Copy-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/12-Copy-scaled.jpg 1316w, https://www.kijeka.com/wp-content/uploads/2021/04/12-Copy-154x300.jpg 154w, https://www.kijeka.com/wp-content/uploads/2021/04/12-Copy-526x1024.jpg 526w, https://www.kijeka.com/wp-content/uploads/2021/04/12-Copy-768x1494.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/12-Copy-789x1536.jpg 789w, https://www.kijeka.com/wp-content/uploads/2021/04/12-Copy-1053x2048.jpg 1053w, https://www.kijeka.com/wp-content/uploads/2021/04/12-Copy-46x90.jpg 46w, https://www.kijeka.com/wp-content/uploads/2021/04/12-Copy-180x350.jpg 180w, https://www.kijeka.com/wp-content/uploads/2021/04/12-Copy-247x480.jpg 247w, https://www.kijeka.com/wp-content/uploads/2021/04/12-Copy-1170x2276.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2021/04/12-Copy-270x525.jpg 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/18-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/18-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/18-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/18-1024x1024.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2021/04/18-768x768.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/18-1536x1536.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2021/04/18-2048x2048.jpg 2048w, https://www.kijeka.com/wp-content/uploads/2021/04/18-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/18-270x270.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/18-370x370.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/18-1170x1170.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2021/04/18-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/11-Copy-2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/11-Copy-2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/11-Copy-2-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/self-supported-movable-folding-ladder/",
                "name": "Self- Supported Movable Folding Ladder",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Ideal for Electrical works, Domestic purpose, or any Industrial job at a height.</li>\n<li>Manufactured from High Tensile Aluminum Alloys.</li>\n<li>An economical variety in aluminum tower, extending section adjusts Intermediately</li>\n<li>Section : Aluminum \u2018C\u2019 section(HE-30 Grade) Size: 66.6mm x 31.25mm</li>\n<li><b>Step Details: Aluminum 63 mm Fully Serrated Steps ensure anti Slip Surface &amp; Firm Grip placed at 10\u2033/12\u2033</b></li>\n<li><b>Wheels &amp; Jacks:\u00a0 Swivel Type 04 Nos. Wheels for Easy Maneuverability &amp; 04 Nos Turn Jacks for Stability\u00a0</b></li>\n<li><strong>Top Platform Size: 18\u2033 x 14\u2033\u00a0</strong></li>\n<li>Other Technical Details: Safety Ring at top, Rubber shoes, M.S hinges etc.</li>\n<li><strong>Available with : 2- Section</strong></li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" style=\"text-align: center;\" width=\"205\"><strong>Available Sizes</strong></td>\n</tr>\n<tr>\n<td width=\"110\"><strong>Closed Height Up to Platform\u00a0</strong></td>\n<td width=\"103\"><strong>Total Ladder </strong><strong>Height</strong></td>\n</tr>\n<tr>\n<td width=\"102\">5 feet</td>\n<td width=\"103\">8 feet</td>\n</tr>\n<tr>\n<td width=\"102\">7 feet</td>\n<td width=\"103\">10 feet</td>\n</tr>\n<tr>\n<td width=\"102\">9 feet</td>\n<td width=\"103\">12 feet</td>\n</tr>\n<tr>\n<td width=\"102\">11 feet</td>\n<td width=\"103\">14 feet</td>\n</tr>\n<tr>\n<td width=\"102\">13 feet</td>\n<td width=\"103\">16 feet</td>\n</tr>\n<tr>\n<td width=\"102\">15 feet</td>\n<td width=\"103\">18 feet</td>\n</tr>\n<tr>\n<td width=\"102\"></td>\n<td width=\"103\"></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-copy-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-copy-scaled.jpg 1266w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-copy-148x300.jpg 148w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-copy-506x1024.jpg 506w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-copy-768x1553.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-copy-760x1536.jpg 760w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-copy-1013x2048.jpg 1013w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-copy-45x90.jpg 45w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-copy-173x350.jpg 173w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-copy-237x480.jpg 237w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-copy-1170x2366.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-copy-270x546.jpg 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-Copy-copy-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-Copy-copy-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-Copy-copy-300x297.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-Copy-copy-70x69.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-Copy-copy-270x267.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-Copy-copy-370x366.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-Copy-copy-170x170.jpg 170w, https://www.kijeka.com/wp-content/uploads/2021/04/IMG_1680-Copy-copy.jpg 383w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/self-supporting-extension-ladders/",
                "name": "Self- Supporting Extension Ladders",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Ideal for Electrical works, Domestic purpose, or any Industrial job at a height.</li>\n<li>Manufactured from High Tensile Aluminium Alloys.</li>\n<li>An economical variety in aluminium tower, extending section adjusts Intermediately</li>\n<li>Elegant, sturdy, light in weight, extremely useful where no wall Support is available to ladders</li>\n<li>Having Solid rubber shoe to avoid surface scratching.</li>\n<li>Section : Aluminium \u2018C\u2019 section(HE-30 Grade) Size: 66.6mm x 31.25mm.</li>\n<li><strong>Ladder Height: As per Below Table</strong></li>\n<li>Step Details: Aluminium 25.5mm Round corrugated tube</li>\n<li>Locking Facility : Aluminium Die Casted catcher (Lockable at every 12inches)</li>\n<li>Operating Facility : Nylon rope &amp; pulleys for extending &amp; closing the ladder</li>\n<li>Top Platform Size: 8\u2033 x 11\u2033(3ft. Below from top)</li>\n<li>Distance between two steps: 12\u2033 Inches c/c</li>\n<li>Confirms to: HE-30grade T-6 Temper, IS : 733 \u2013 1982</li>\n<li>Other Technical Details: Safety Ring at top, Rubber shoes, M.S hinges etc.</li>\n</ul>\n<ul>\n<li><strong>Available with : 2- Section</strong></li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"205\"><strong>Available Sizes\u00a0</strong><strong>In\u00a0</strong><strong>2-Section </strong></td>\n</tr>\n<tr>\n<td width=\"110\"><strong>Closed Height</strong></td>\n<td width=\"103\"><strong>Extended\u00a0</strong><strong>Height</strong></td>\n</tr>\n<tr>\n<td width=\"102\">8 ft.</td>\n<td width=\"103\">14 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">10 ft.</td>\n<td width=\"103\">17 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">12 ft.</td>\n<td width=\"103\">21 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">14 ft.</td>\n<td width=\"103\">25 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">16 ft.</td>\n<td width=\"103\">29 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">18 ft.</td>\n<td width=\"103\">32 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">20 ft.</td>\n<td width=\"103\">35 ft.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Self-Supporting-Extension-Ladders.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/self-supporting-ladders/",
                "name": "Self-Supporting Ladders",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Manufactured from high tensile aluminum alloy</li>\n<li>Compact, light\u00a0in weight yet sturdy, foldable and suitable where no wall support is available.</li>\n<li>Platform\u00a0on top\u00a0for convenient working.</li>\n<li>Section Size Width: Aluminium \u201cC\u201d Section(HE-30 Grade) Size: 66.6mm x 31.25mm</li>\n<li>Material Standard: Confirm HE-30 Grade T-6 Temper, IS 733-1982</li>\n<li>Step Details: Anti Slip 5 Inch Aluminium Flat Steps</li>\n<li>Distance Between Two Steps- 12\u201d Centre to Centre</li>\n<li>Solid Robber Shoes At Bottom to avoid surface scratching</li>\n<li><strong>Available Sizes : 6 Feet, 8 Feet, 10 Feet, 12 Feet, 14 Feet, 15 Feet, 16 Feet, 18 Feet, 20 Feet</strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Self-Supporting-Ladders.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Self-Supporting-Ladders.png 257w, https://www.kijeka.com/wp-content/uploads/2017/10/Self-Supporting-Ladders-180x300.png 180w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/step-ladders/",
                "name": "Step Ladders",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Step ladder is made from high tensile aluminium alloy.</li>\n<li>Tubular pipe structure, platform for standing with guard rails</li>\n<li>80 mm steps with non-slip ribbed surface, slip resistant shoes, sophisticated, elegant look.</li>\n<li>Extremely light weight.</li>\n<li><strong>Available Sizes : 3 Steep, 4 Steep, 5 Steep, 6 Steep, 7 Steep</strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/step_ladder.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/step_ladder.png 278w, https://www.kijeka.com/wp-content/uploads/2017/10/step_ladder-180x300.png 180w, https://www.kijeka.com/wp-content/uploads/2017/10/step_ladder-270x450.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/til-table-tower-ladders/",
                "name": "Til table Tower Ladders",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Manufactured from High Tensile Aluminium Alloys</li>\n<li><strong>It is designed to suit low passages and overhead obstructions as the Structure is tilt able into horizontal position.</strong></li>\n<li>Section Size Width: Aluminium \u201cC\u201d Section(HE-30 Grade) Size: 66.6mm x 31.25mm</li>\n<li>Material Standard: Confirm HE-30 Grade T-6 Temper, IS 733-1982</li>\n<li>Ladder Base Material MOC : Heavy Duty MS Channel &amp; MS Angles</li>\n<li>Step Details: Aluminum 25.4 mm Round Corrugated Tubes</li>\n<li>Distance Between Two Steps- 12\u201d Centre to Centre</li>\n<li>Locking Facility: Pendulum Lock, Winch Gear Equipped with Dual Locking Facilities</li>\n<li>Operating Facility: 01 No. Winch Gear Machine with required Wire Rope &amp; Pulleys for Extending &amp; Closing the Ladder</li>\n<li>Mechanism for Tilting: 01 No. Winch Gear for Tilting the Ladder</li>\n<li>Size Of Top Platform: 18\u201d X 21\u201d (3-feet Below from Top)</li>\n<li>Wheel Option: Available with Solid Hard Polymer, Rubber Or Pneumatic Rubber Wheels</li>\n<li><strong>Having 4-jacks for braking as well as levelling purpose.</strong></li>\n<li>Other Features: Tool Try on Top, Safety Stoppers, Safety Belt, Safety Helmet,</li>\n<li><strong>Available with : 2- Section &amp; 3- Section </strong></li>\n</ul>\n<p><strong>\u00a0</strong></p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"208\"><strong>Available Sizes\u00a0</strong><strong>In\u00a0</strong><strong style=\"font-family: inherit; font-size: inherit;\">2- Section</strong></td>\n</tr>\n<tr>\n<td width=\"106\"><strong>Closed Height</strong></td>\n<td width=\"103\"><strong>Extended\u00a0</strong><strong>Height</strong></td>\n</tr>\n<tr>\n<td width=\"102\">8 ft.</td>\n<td width=\"103\">14 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">10 ft.</td>\n<td width=\"103\">17 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">12 ft.</td>\n<td width=\"103\">21 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">14 ft.</td>\n<td width=\"103\">25 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">16 ft.</td>\n<td width=\"103\">29 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">18 ft.</td>\n<td width=\"103\">32 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">20 ft.</td>\n<td width=\"103\">35 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">24 ft.</td>\n<td width=\"103\">43 ft.</td>\n</tr>\n</tbody>\n</table>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"208\"><strong>Available Sizes\u00a0</strong><strong>In\u00a0</strong><strong>3- Section</strong></td>\n</tr>\n<tr>\n<td width=\"106\"><strong>Closed\u00a0</strong><strong>Height</strong></td>\n<td width=\"102\"><strong>Extended\u00a0</strong><strong>Height</strong></td>\n</tr>\n<tr>\n<td width=\"106\">12 ft.</td>\n<td width=\"102\">30 ft.</td>\n</tr>\n<tr>\n<td width=\"106\">14 ft.</td>\n<td width=\"102\">36 ft.</td>\n</tr>\n<tr>\n<td width=\"106\">16 ft.</td>\n<td width=\"102\">40 ft.</td>\n</tr>\n<tr>\n<td width=\"106\">20 ft.</td>\n<td width=\"102\">50 ft.</td>\n</tr>\n<tr>\n<td width=\"106\">24 ft.</td>\n<td width=\"102\">60 ft.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Til-table-Tower-Ladders.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Til-table-Tower-Ladders.png 270w, https://www.kijeka.com/wp-content/uploads/2017/10/Til-table-Tower-Ladders-185x300.png 185w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/trestle-flat-step-ladder/",
                "name": "Trestle Flat Step Ladder",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Manufactured from high tensile aluminum alloy</li>\n<li>Compact, light\u00a0in weight yet sturdy, foldable and suitable where no wall support is available.</li>\n<li>Platform\u00a0on top\u00a0for convenient working.</li>\n<li>Section Size Width: Aluminium \u201cC\u201d Section(HE-30 Grade) Size: 66.6mm x 31.25mm</li>\n<li>Material Standard: Confirm HE-30 Grade T-6 Temper, IS 733-1982</li>\n<li>Step Details: Anti Slip 5 Inch Aluminium Flat Steps</li>\n<li>Distance Between Two Steps- 12\u201d Centre to Centre</li>\n<li>Solid Robber Shoes At Bottom to avoid surface scratching</li>\n<li><strong>Available Sizes : 6 Feet, 8 Feet, 10 Feet, 12 Feet, 14 Feet, 15 Feet, 16 Feet, 18 Feet, 20 Feet</strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Self-Supporting-Ladders.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Self-Supporting-Ladders.png 257w, https://www.kijeka.com/wp-content/uploads/2017/10/Self-Supporting-Ladders-180x300.png 180w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/trestle-round-step-ladder/",
                "name": "Trestle Round Step Ladder",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Manufactured from high tensile aluminum alloy</li>\n<li>Compact, light\u00a0in weight yet sturdy, foldable and suitable where no wall support is available.</li>\n<li>Platform\u00a0on top\u00a0for convenient working.</li>\n<li>Section Size Width: Aluminum \u201cC\u201d Section(HE-30 Grade) Size: 66.6mm x 31.25mm</li>\n<li>Material Standard: Confirm HE-30 Grade T-6 Temper, IS 733-1982</li>\n<li><strong>Top Platform Size:</strong> 10\u2033x16\u2033 Slip Resistant Platform on Top\u00a0 for convenient Working</li>\n<li><strong>Step Details:</strong> Anti Slip 1\u2033Corrugated Round Steps ensures anti-Slip Surface &amp; Firm Grip</li>\n<li>Distance Between Two Steps- 10\u2033/12\u201d Centre to Centre</li>\n<li>Solid Robber Shoes At Bottom to avoid surface scratching</li>\n<li><strong>Available Sizes :5, 6, 8, 10, 12, 14, 15, 16, 18, 20 Feet</strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Trestle-Round-Step-Ladder.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Trestle-Round-Step-Ladder.jpg 600w, https://www.kijeka.com/wp-content/uploads/2021/04/Trestle-Round-Step-Ladder-199x300.jpg 199w, https://www.kijeka.com/wp-content/uploads/2021/04/Trestle-Round-Step-Ladder-60x90.jpg 60w, https://www.kijeka.com/wp-content/uploads/2021/04/Trestle-Round-Step-Ladder-232x350.jpg 232w, https://www.kijeka.com/wp-content/uploads/2021/04/Trestle-Round-Step-Ladder-318x480.jpg 318w, https://www.kijeka.com/wp-content/uploads/2021/04/Trestle-Round-Step-Ladder-270x408.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/trolley-step-ladder/",
                "name": "Trolley Step Ladder",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Manufactured from high tensile aluminium alloy</li>\n<li>Trolley Step Ladder is designed for comfortable working at Heights with its cubical Platform</li>\n<li>Ladder having 2.5\u201d Inch wide anti slip Steps</li>\n<li>Ladder Based on M.S. Channel fitted with 2-swivelling Brake Type Caster &amp; 2-fixed type casters for easy manoeuvrability.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td width=\"234\"><strong>Particular Section / Part </strong></td>\n<td width=\"367\"><strong>Description / Size</strong></td>\n</tr>\n<tr>\n<td width=\"234\">Size of Platform</td>\n<td width=\"367\">18\u201d Inch\u00a0 X 24\u201d Inch</td>\n</tr>\n<tr>\n<td width=\"234\">Ladder Step Details</td>\n<td width=\"367\">2.5\u201d Inch Aluminium Flat Step</td>\n</tr>\n<tr>\n<td width=\"234\">Distance Between Two Steps</td>\n<td width=\"367\">12\u201d Inches C/C</td>\n</tr>\n<tr>\n<td width=\"234\">Side Section Dimensions</td>\n<td width=\"367\">Size: 66.6 mm\u00a0 X 31.25 mm ( HE-30 Grade) Aluminium \u2019C\u2019 Section</td>\n</tr>\n<tr>\n<td width=\"234\">Base Frame\u00a0 MOC</td>\n<td width=\"367\">MS Channel 75mm x 40 mm</td>\n</tr>\n<tr>\n<td width=\"234\">Caster Wheel Details</td>\n<td width=\"367\">Nylon Caster Wheels -04 Nos ( 2- Swivel + 2- Fix Type)</td>\n</tr>\n<tr>\n<td width=\"234\">Top Railing/ Safety Railing</td>\n<td width=\"367\">MS Railing of 2 feet above the Top Platform</td>\n</tr>\n<tr>\n<td width=\"234\">Confirms to</td>\n<td width=\"367\">HE-30 GRADE, T-6 Temper, IS: 733-1982</td>\n</tr>\n<tr>\n<td width=\"234\">Available Height</td>\n<td width=\"367\">4 Feet, 6 Feet, 8 Feet, 10 Feet- Up to Platform</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Trolley-Step-Ladder.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Trolley-Step-Ladder.png 324w, https://www.kijeka.com/wp-content/uploads/2017/12/Trolley-Step-Ladder-184x300.png 184w, https://www.kijeka.com/wp-content/uploads/2017/12/Trolley-Step-Ladder-270x440.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/wall-supporting-extension-ladders/",
                "name": "Wall Supporting Extension Ladders",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Manufactured from high tensile aluminum alloy</li>\n<li>Section Size Width: Aluminium \u201cC\u201d Section(HE-30 Grade) Size: 66.6mm x 31.25mm</li>\n<li>Material Standard: Confirm HE-30 Grade T-6 Temper, IS 733-1982</li>\n<li>Step Details: Aluminum 25.4 mm Round Corrugated Tubes</li>\n<li>Distance Between Two Steps- 12\u201d Centre to Centre</li>\n<li>Locking Facility: Aluminium Die Casted Catcher ( Lockable at Every 12\u201d)</li>\n<li>Operating Facility: Nylon Rope &amp; Pulleys For Extension &amp; Closing the Ladder</li>\n<li>Solid Robber Shoes At Bottom to avoid surface scratching</li>\n<li><strong>Available with : 2- Section &amp; 3- Section </strong></li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"220\"><strong>Available Sizes\u00a0</strong><strong>In\u00a0</strong><strong style=\"font-family: inherit; font-size: inherit;\">2- Section</strong></td>\n</tr>\n<tr>\n<td width=\"110\"><strong>Closed Height</strong></td>\n<td width=\"110\"><strong>Extended\u00a0</strong><strong>Height</strong></td>\n</tr>\n<tr>\n<td width=\"102\">8 ft.</td>\n<td width=\"103\">14 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">10 ft.</td>\n<td width=\"103\">17 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">12 ft.</td>\n<td width=\"103\">21 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">14 ft.</td>\n<td width=\"103\">25 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">16 ft.</td>\n<td width=\"103\">29 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">18 ft.</td>\n<td width=\"103\">32 ft.</td>\n</tr>\n<tr>\n<td width=\"102\">20 ft.</td>\n<td width=\"103\">35 ft.</td>\n</tr>\n</tbody>\n</table>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"220\"><strong>Available Sizes\u00a0</strong><strong>In\u00a0</strong><strong>3- Section</strong></td>\n</tr>\n<tr>\n<td width=\"110\"><strong>Closed Height</strong></td>\n<td width=\"130\"><strong>Extended Height</strong></td>\n</tr>\n<tr>\n<td width=\"106\">10 ft.</td>\n<td width=\"102\">24 ft.</td>\n</tr>\n<tr>\n<td width=\"106\">12 ft.</td>\n<td width=\"102\">30 ft.</td>\n</tr>\n<tr>\n<td width=\"106\">14 ft.</td>\n<td width=\"102\">36 ft.</td>\n</tr>\n<tr>\n<td width=\"106\">16 ft.</td>\n<td width=\"102\">40 ft.</td>\n</tr>\n<tr>\n<td width=\"106\">20 ft.</td>\n<td width=\"102\">50 ft.</td>\n</tr>\n<tr>\n<td width=\"106\">24 ft.</td>\n<td width=\"102\">60 ft.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wall-Supporting-Extension-Ladders.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wall-Supporting-Extension-Ladders.png 194w, https://www.kijeka.com/wp-content/uploads/2017/10/Wall-Supporting-Extension-Ladders-142x300.png 142w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/wall-supporting-ladders/",
                "name": "Wall Supporting Ladders Flat Step",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Manufactured from high tensile aluminum alloy</li>\n<li>Section Size Width: Aluminium \u201cC\u201d Section(HE-30 Grade) Size: 66.6mm x 31.25mm</li>\n<li>Material Standard: Confirm HE-30 Grade T-6 Temper, IS 733-1982</li>\n<li>Step Details: Anti Slip 2.5 Inch Aluminium Flat Steps</li>\n<li>Distance Between Two Steps- 12\u201d Centre to Centre</li>\n<li>Solid Robber Shoes At Bottom to avoid surface scratching</li>\n<li>Available with \u201cJ\u201d Or \u201cL\u201d Type Hook at the Top of Ladder</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/05/Wall-Supporting-Ladders.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/05/Wall-Supporting-Ladders.png 288w, https://www.kijeka.com/wp-content/uploads/2017/05/Wall-Supporting-Ladders-154x300.png 154w, https://www.kijeka.com/wp-content/uploads/2017/05/Wall-Supporting-Ladders-270x525.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/wall-supporting-ladders-2/",
                "name": "Wall Supporting Ladders Round Step",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Wall Supporting Ladders Aluminum Single Ladder Manufactured from C Section of 67x31x3mm</li>\n<li>Material Standard: Confirm HE-30 Grade T-6 Temper, IS 733-1982</li>\n<li>Distance Between Two Steps- 12\u201d Centre to Centre</li>\n<li>Step Details: 25.4mm <strong>Dia Round Corrugated Steps</strong></li>\n<li>Solid Robber Shoes At Bottom to avoid surface scratching</li>\n<li>Available with <strong>\u201cJ\u201d Or \u201cL\u201d</strong> Type Hook at the Top of Ladder</li>\n<li><strong>Available Height:</strong> 5,6,8,10,12,14,16,18,20feets</li>\n</ul>\n</div>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Supporting-Ladders-Round-Step.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Supporting-Ladders-Round-Step.jpg 600w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Supporting-Ladders-Round-Step-225x300.jpg 225w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Supporting-Ladders-Round-Step-68x90.jpg 68w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Supporting-Ladders-Round-Step-263x350.jpg 263w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Supporting-Ladders-Round-Step-360x480.jpg 360w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Supporting-Ladders-Round-Step-270x360.jpg 270w"
                    ]
                ]
            }
        ],
        "Chemical Pumps & Acces.": [
            {
                "link": "https://www.kijeka.com/product/air-operated-double-diaphragm-aodd-pumps/",
                "name": "AODD Pumps (Air Operated Double Diaphragm Pump)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>The only fuel required for AODD pumps are compressed air. AODD pumps do not require the use of electricity or any other fuel source that may pose a risk for working employees who operate or use them on a daily basis. This works as an added benefit for the food and beverage industry</li>\n<li>AODD pumps offer a number of advantages that make them perfect for an almost endless variety of uses.</li>\n<li>AODD Pumps Can easily and efficiently handle anything from water to 90% solids</li>\n<li>The AODD pumps are able to run dry without damaging costly internal wear parts or destroying an expensive motor, One pump to be used for numerous applications, eliminating the need for expensive motor drives and critical sizing calculations</li>\n<li>They are used for a number of applications across a wide range of industries including oil and gas, Vehicle Production &amp; Maintenance, Construction &amp; Mining,\u00a0Print &amp; Packaging , Pulp &amp; Paper Converters,\u00a0 Paint &amp; Coating, Process Water, Wastewater, Surface Treatment, Chemical, Petrochemical, Refinery, Food processing&amp; Hygienic Applications\u00a0 ,Ceramic slip &amp; Glaze, Electronics, Pharmaceuticals etc.. etc..</li>\n</ul>\n<p><strong>Available Range:</strong></p>\n<ul>\n<li><strong>MOC:</strong> Hygienic 316, Stainless Steel, Aluminium, Cast Iron, Polypropylene &amp; PVDF</li>\n<li><strong>Size:</strong> 1/2\u201d,1\u201d,1 \u00bd\u201d,2\u201d Size</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Air-operated-double-diaphragm-AODD-pumps2.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Air-operated-double-diaphragm-AODD-pumps2.png 167w, https://www.kijeka.com/wp-content/uploads/2017/06/Air-operated-double-diaphragm-AODD-pumps2-70x90.png 70w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/AODD-Pump.-KE213-DF50PBYTWTTBAS-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/AODD-Pump.-KE213-DF50PBYTWTTBAS-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/AODD-Pump.-KE213-DF50PBYTWTTBAS-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/AODD-Pump.-KE213-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/AODD-Pump.-KE213-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/AODD-Pump.-KE213-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Air-operated-double-diaphragm-AODD-pumps1-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Air-operated-double-diaphragm-AODD-pumps1-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Air-operated-double-diaphragm-AODD-pumps1-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/dosing-metering-pumps-dosing-system/",
                "name": "Dosing-Metering Pumps & Dosing System",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Dosing \u2013 Metering Pump is single acting reciprocating type positive displacement controlled volume pump which can deliver flow streams at adjustable &amp; controlled rates in required process conditions.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"564\">\n<tbody>\n<tr>\n<td width=\"180\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"384\"><strong>Dosing-Metering Pumps.</strong></td>\n</tr>\n<tr>\n<td width=\"180\">Capacity</td>\n<td width=\"384\">100 ml/hr to 15000 LPH</td>\n</tr>\n<tr>\n<td width=\"180\">Head</td>\n<td width=\"384\">Up to 1000 Kg/cm<sup>2</sup></td>\n</tr>\n<tr>\n<td width=\"180\">Manufacturing Standard</td>\n<td width=\"384\">API \u2013675</td>\n</tr>\n<tr>\n<td width=\"180\">MOC</td>\n<td width=\"384\">AISI 316, AISI 304, AISI 410, CS, Alloy-20,\n<p>Hastelloy C &amp; B, Titanium, Monel, Polypropylene, PTFE, Nylon, PVC, UHMWPE, etc.</p></td>\n</tr>\n<tr>\n<td width=\"180\">Temperature</td>\n<td width=\"384\">30<sup>o</sup>C to 150<sup>o</sup>C</td>\n</tr>\n<tr>\n<td width=\"180\">Stroke Adjustment Cartridge</td>\n<td width=\"384\">Manual, Pneumatic, and Electric</td>\n</tr>\n<tr>\n<td width=\"180\">Wet End Cartridge</td>\n<td width=\"384\">Single acting or double acting plunger, Mechanically actuated diaphragm,\u00a0 Hydraulically actuated single or double diaphragm Bellow, Wet end\u00a0 cartridge with heating or cooling jacket</td>\n</tr>\n<tr>\n<td width=\"180\">Valve</td>\n<td width=\"384\">Ball, Cone, Plate, Wing with or without spring loaded.</td>\n</tr>\n<tr>\n<td width=\"180\">Gland Packing</td>\n<td width=\"384\">U seal (PTFE, Chevron, PU) , Square rope, Bellow type</td>\n</tr>\n<tr>\n<td width=\"180\">Options</td>\n<td width=\"384\">Pressure relief valve, Pulsation dampener, instrumentation\n<p>And automation, complete dosing systems</p></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps4.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps4.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps4-300x213.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps4-768x546.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps4-70x50.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps4-270x192.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps4-370x263.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps3-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps3-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps3-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps5-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps5-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps5-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps13-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps13-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Dosing-Metering-Pumps13-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/external-rotary-gear-pumps/",
                "name": "External Rotary Gear Pumps",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>These are the most commonly used light duty all-purpose pumps for Handling and Transferring variety of Viscous Liquids, may these be Oils, Petroleum, Dairy &amp; Food Products, Dyes, Syrups, Slightly Corrosive Chemicals, Soaps, Detergents, Starch, Asphalts, Inks and Paints etc.</li>\n<li>The self-lubricated bush bearing type design ensures longer life of pumps</li>\n<li>All pumps are provided with built-in pressure relief valve.</li>\n<li>The shaft sealing is by Rubber oil seals, which\u00a0ensures leak proof working than gland packing design. The alternative sealing like Z- Pack\u00a0 or\u00a0 Mechanical Seal will be is provided on depends of liquid characteristics or on request</li>\n<li>Jacketed features for handling Tar, Bitumen, Asphalts, Wax, Soaps, etc. liquids.</li>\n<li>External\u00a0/ Internal Ball / Needle Bearings type gear pumps are available as an optional on request.</li>\n<li>Simple , Compact , Robust design Hence longest service life</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"564\">\n<tbody>\n<tr>\n<td width=\"164\">\n<p style=\"text-align: center;\"><strong>Model \u00a0</strong></p>\n</td>\n<td width=\"400\"><strong>External Rotary Gear Pumps.</strong></td>\n</tr>\n<tr>\n<td width=\"164\">Capacity</td>\n<td width=\"400\">Up to 850 Liters / Minute</td>\n</tr>\n<tr>\n<td width=\"164\">Head</td>\n<td width=\"400\">Up to 12 Kg/Cm2 pressure</td>\n</tr>\n<tr>\n<td width=\"164\">Size</td>\n<td width=\"400\">\u00bc\u201d to 4\u201d</td>\n</tr>\n<tr>\n<td width=\"164\">Pump Speed</td>\n<td width=\"400\">Max. 1440 rpm</td>\n</tr>\n<tr>\n<td width=\"164\">MOC</td>\n<td width=\"400\">Std. Cast Iron, Cast Iron /SS, Carbon Steel, Gun Metal, SS 316, SS 304 etc\u2026</td>\n</tr>\n<tr>\n<td width=\"164\">Temperature</td>\n<td width=\"400\">90\u00b0 C , Modified Version 250\u00b0</td>\n</tr>\n<tr>\n<td width=\"164\">Viscosity\u00a0 Range</td>\n<td width=\"400\">Up to 10,000 cst</td>\n</tr>\n<tr>\n<td width=\"164\">Major Application\n<p>\u00a0</p></td>\n<td width=\"400\">All types of Oils &amp; Viscous liquids like All Fuel Oils, Mineral Oils, Lubricating Oils, Fish and Animal Oils, Vegetable Oils, Tar, Asphalts, Sugar Syrups, Molasses, Starch, Soaps, Silicate, Wood Pulp, Glycol, Glycerine, Honey, Inks, Colours &amp; Paints, Resins, Kerosene,\u00a0 Varnishes and viscous chemicals etc.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/External-Rotary-Gear-Pump85-1.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/External-Rotary-Gear-Pump85-1.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/External-Rotary-Gear-Pump85-1-300x179.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/External-Rotary-Gear-Pump85-1-768x458.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/External-Rotary-Gear-Pump85-1-70x42.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/External-Rotary-Gear-Pump85-1-270x161.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/External-Rotary-Gear-Pump85-1-370x221.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/hand-flow-regulator/",
                "name": "Hand Flow Regulator",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Hand Flow Regulator is a flow controlling device designed especially for flow control.</li>\n<li>Made out from Stainless Steel 316 fitted with Teflon Seals</li>\n<li>Designed exclusively for the stringent requirements of Fragrances and Flavor industries.</li>\n<li>Hand Flow Regulator is a compact, lightweight solution to packing of small volume containers.</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Facucet851.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Facucet851.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Facucet851-300x203.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Facucet851-768x520.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Facucet851-70x47.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Facucet851-270x183.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Facucet851-370x250.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/high-pressure-plunger-pumps/",
                "name": "High Pressure Plunger Pumps",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>High Pressure Plunger pump is a type of positive displacement pump where the high-pressure seal is stationary and a smooth cylindrical plunger slides though the seal. This makes them different from <a href=\"http://en.wikipedia.org/wiki/Piston_pump\">piston pumps</a> and allows them to be used at high pressures.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"593\">\n<tbody>\n<tr>\n<td width=\"193\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"400\"><strong>\u00a0 High Pressure Plunger Pumps.</strong></td>\n</tr>\n<tr>\n<td width=\"193\">Flow Range</td>\n<td width=\"400\">\u00a0 Up to 30,000 LPH</td>\n</tr>\n<tr>\n<td width=\"193\">Pressure Range</td>\n<td width=\"400\">\u00a0 Up to 1000 Kg/cm2</td>\n</tr>\n<tr>\n<td width=\"193\">Temperature Range</td>\n<td width=\"400\">\u00a0 30<sup>o</sup> C to 300<sup>o</sup> C</td>\n</tr>\n<tr>\n<td width=\"193\">Standard</td>\n<td width=\"400\">\u00a0 API \u2013674</td>\n</tr>\n<tr>\n<td width=\"193\">MOC</td>\n<td width=\"400\">\u00a0AISI 316, AISI 304, AISI 410</td>\n</tr>\n<tr>\n<td width=\"193\">Wet End Cartridge</td>\n<td width=\"400\">\u00a0Single / Double Acting ( Simplex/ Duplex / Triplex ) Plunger</td>\n</tr>\n<tr>\n<td width=\"193\">Valve</td>\n<td width=\"400\">\u00a0Ball, Cone, Plate, Wing with or without spring loaded.</td>\n</tr>\n<tr>\n<td width=\"193\">Gland Packing</td>\n<td width=\"400\">\u00a0U seal (PTFE, Chevron, PU) , Square Rope.</td>\n</tr>\n<tr>\n<td width=\"193\">Options</td>\n<td width=\"400\">\u00a0Pressure Relief Valve, Pulsation Dampener, Instrumentation\n<p>and Automation , Complete Pumping Systems</p></td>\n</tr>\n<tr>\n<td width=\"193\">Drive</td>\n<td width=\"400\">Electric Motor, Engine or Hydraulic Drive</td>\n</tr>\n<tr>\n<td width=\"193\">Major Application\n<p>\u00a0</p></td>\n<td width=\"400\">Hydro Test Application, Reverse Osmosis, Boiler Feed, Pressure Washing, Misting / Cooling / Fogging, Positive Displacement, Sewer Jetting,\u00a0 Agriculture; High Pressure Coolant, Special Industry\n<p>\u00a0</p></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/High-Pressure-Plunger-Pumps1.png"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/High-Pressure-Plunger-Pumps2-150x133.png"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/High-Pressure-Plunger-Pumps5-150x134.png"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/High-Pressure-Plunger-Pumps4-150x119.png"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/High-Pressure-Plunger-Pumps3-150x135.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/high-viscous-liquid-transfer-drum-pump/",
                "name": "High Viscous Liquid Transfer Drum Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Progressing Cavity Type Screw Pumpsare designed for pumping light to highly viscous liquids. The progressing cavity design ensures smooth and non-pulsating flow and ideal for the gentle transfer of viscous liquids.</li>\n<li>High Viscosity Liquid Pump is especially suitable for viscous liquids such as Liquid Soap, Plastic Solutions, Synthetic Resin, Glues, Molasses, Syrups, Liquid Chocolate, Honey, Glycerin etc. etc\u2026</li>\n<li><strong>Working Principle: </strong>Pumping action starts the instant, the ROTOR turns. Liquid enters the pump Suction under pressure as the ROTOR turns within the STATOR thus forming tightly sealed Cavities which moves the liquid toward the Outlet. Liquid acts as lubricant between the rotor and Stator</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>High Viscous Liquid Transfer from the Drum/ Barrel</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"664\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"161\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"266\"><strong>High Viscous Liquid Transfer</strong>\n<p><strong>Electric Drum Pump.</strong></p></td>\n<td width=\"237\"><strong>High Viscous Liquid Transfer</strong>\n<p><strong>Pneumatic Drum Pump.</strong></p></td>\n</tr>\n<tr>\n<td width=\"102\">Pump MOC</td>\n<td width=\"59\"></td>\n<td width=\"266\">SS 316</td>\n<td width=\"237\">SS 316</td>\n</tr>\n<tr>\n<td width=\"102\">Pump Rotor</td>\n<td width=\"59\"></td>\n<td width=\"266\">SS 316 Screw</td>\n<td width=\"237\">SS 316 Screw</td>\n</tr>\n<tr>\n<td width=\"102\">Stator MOC</td>\n<td width=\"59\"></td>\n<td width=\"266\">SS 316 Pipe with\u00a0 internally moulded synthetic rubber &amp;<u>Available in Viton, Hypalon, Neoprene, EPDM, Buna \u2013N.</u></td>\n<td width=\"237\">SS 316 Pipe with\u00a0 internally moulded synthetic rubber &amp;<u>Available in Viton, Hypalan, Neoprene, EPDM, Buna \u2013N</u>.</td>\n</tr>\n<tr>\n<td width=\"102\">Drive Type</td>\n<td width=\"59\"></td>\n<td width=\"266\">Electric Motor ( Detachable)</td>\n<td width=\"237\">Air\u00a0 Motor ( Detachable)</td>\n</tr>\n<tr>\n<td width=\"102\">Drive Option</td>\n<td width=\"59\"></td>\n<td width=\"266\">Flameproof Electric &amp; Non- Flameproof</td>\n<td width=\"237\">Flameproof Air Motor</td>\n</tr>\n<tr>\n<td width=\"102\">Capacity</td>\n<td width=\"59\">Kg/Min.</td>\n<td width=\"266\">Maximum 40</td>\n<td width=\"237\">Maximum 25</td>\n</tr>\n<tr>\n<td width=\"102\">Head</td>\n<td width=\"59\">Bar</td>\n<td width=\"266\">Maximum 8 Bar</td>\n<td width=\"237\">Maximum 6 Bar</td>\n</tr>\n<tr>\n<td width=\"102\">Suction Tube Length</td>\n<td width=\"59\">mm</td>\n<td width=\"266\">990 mm</td>\n<td width=\"237\">990 mm</td>\n</tr>\n<tr>\n<td width=\"102\">Suction Tube\n<p>Diameter</p></td>\n<td width=\"59\">mm</td>\n<td width=\"266\">Available in 44 MM, 51MM</td>\n<td width=\"237\">Available in 44 MM, 51MM</td>\n</tr>\n<tr>\n<td width=\"102\">Discharge Size</td>\n<td width=\"59\">mm</td>\n<td width=\"266\">44mm</td>\n<td width=\"237\">44mm</td>\n</tr>\n<tr>\n<td width=\"102\">Viscosity Range</td>\n<td width=\"59\">centiPoise (cP)</td>\n<td width=\"266\">\u00a025000 cP</td>\n<td width=\"237\">7000 cP</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump3.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump3.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump3-212x300.jpg 212w, https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump3-768x1087.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump3-724x1024.jpg 724w, https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump3-64x90.jpg 64w, https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump3-247x350.jpg 247w, https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump3-339x480.jpg 339w, https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump3-270x382.jpg 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump2-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/High-Viscous-Liquid-Transfer-Drum-Pump-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/low-viscous-liquid-transfer-drum-pump/",
                "name": "Low Viscous Liquid Transfer Drum Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Low Viscous Drum Pump, the customer focused and user friendly, handles a wide range of chemicals from strong Acids and Caustic to severe Solvents, Fragrances, Flavours and Essential Oils.</li>\n<li><strong>Working Principle: </strong>The pump tube is connected to motor by means of self aligning coupling. The motor transmits power through coupling to the drive shaft of pump which is well supported by TEFLON tube, bearing. The impeller is mounted at the foot piece of the pump tube and is always immersed in the liquid which assures self-priming.</li>\n</ul>\n<p><u>\u00a0</u></p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Low Viscous Liquid Transfer from the Drum/ Barrel</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"664\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"161\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"266\"><strong>Low Viscous Liquid Transfer</strong>\n<p><strong>Electric Drum Pump.</strong></p></td>\n<td width=\"237\"><strong>Low Viscous Liquid Transfer</strong>\n<p><strong>Pneumatic Drum Pump.</strong></p></td>\n</tr>\n<tr>\n<td width=\"102\">Pump MOC</td>\n<td width=\"59\"></td>\n<td width=\"266\">SS 316 Or Polypropylene</td>\n<td width=\"237\">SS 316 \u00a0Or Polypropylene</td>\n</tr>\n<tr>\n<td width=\"102\">Drive Type</td>\n<td width=\"59\"></td>\n<td width=\"266\">Electric Motor ( Detachable)</td>\n<td width=\"237\">Air\u00a0 Motor ( Detachable)</td>\n</tr>\n<tr>\n<td width=\"102\">Drive Option</td>\n<td width=\"59\"></td>\n<td width=\"266\">Flameproof Electric &amp; Non- Flameproof</td>\n<td width=\"237\">Flameproof Air Motor</td>\n</tr>\n<tr>\n<td width=\"102\">Capacity</td>\n<td width=\"59\">Litre/Min.</td>\n<td width=\"266\">Maximum 70 LPM@Open Discharge</td>\n<td width=\"237\">Maximum 70 LPM@Open Discharge</td>\n</tr>\n<tr>\n<td width=\"102\">Head</td>\n<td width=\"59\">Meter</td>\n<td width=\"266\">Maximum 12 Meter</td>\n<td width=\"237\">Maximum 12 Meter</td>\n</tr>\n<tr>\n<td width=\"102\">Suction Tube Length</td>\n<td width=\"59\">mm</td>\n<td width=\"266\">990 mm</td>\n<td width=\"237\">990 mm</td>\n</tr>\n<tr>\n<td width=\"102\">Suction Tube\n<p>Diameter</p></td>\n<td width=\"59\">mm</td>\n<td width=\"266\">Available in 44 MM</td>\n<td width=\"237\">Available in 44 MM</td>\n</tr>\n<tr>\n<td width=\"102\">Discharge Size</td>\n<td width=\"59\">mm</td>\n<td width=\"266\">44mm</td>\n<td width=\"237\">44mm</td>\n</tr>\n<tr>\n<td width=\"102\">Pump Seal</td>\n<td width=\"59\"></td>\n<td width=\"266\">\u00a0Viton Or EPDM</td>\n<td width=\"237\">Viton Or EPDM</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Low-Viscous-Liquid-Transfer-Drum-Pump.png"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Low-Viscous-Liquid-Transfer-Drum-Pump-2.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/nylon-chemical-pump/",
                "name": "Nylon Chemical Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Self-Priming Vertical Lift Pump designed for use with Lacquers, Thinners, urea etc\u2026</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"545\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"329\"><strong>Nylon Chemical Pump.</strong></td>\n</tr>\n<tr>\n<td width=\"186\">Wetted\u00a0 Components</td>\n<td width=\"30\"></td>\n<td width=\"329\">Nylon, Polypropylene, Stainless Steel &amp; PTFE</td>\n</tr>\n<tr>\n<td width=\"186\">Drive Type</td>\n<td width=\"30\"></td>\n<td width=\"329\">\u00a0\u00a0\u00a0 Manual/ Hand Operated</td>\n</tr>\n<tr>\n<td width=\"186\">Recommended Use</td>\n<td width=\"30\"></td>\n<td width=\"329\">Water-based media, detergents, Thinners, Glycerine, Water, Weed Killer, Brake Kleen, Mild Acids, Petroleum Based Media</td>\n</tr>\n<tr>\n<td width=\"186\"><strong>Do Not Use With </strong></td>\n<td width=\"30\"></td>\n<td width=\"329\">Strong Acids, Bleach &amp; Petrol</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Nylon-Chemical-Pumps-scaled.jpg"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/plastic-lever-pump/",
                "name": "Plastic Lever Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Lever Action Pump designed for use with Viscous Oils, Thick fluid &amp; Agricultural Chemicals.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"545\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"329\"><strong>Plastic Lever Pump.</strong></td>\n</tr>\n<tr>\n<td width=\"186\">Wetted\u00a0 Components</td>\n<td width=\"30\"></td>\n<td width=\"329\">Polyacetal, polypropylene, polyethylene, PVC &amp;\n<p>Viton</p></td>\n</tr>\n<tr>\n<td width=\"186\">Drive Type</td>\n<td width=\"30\"></td>\n<td width=\"329\">Manual/ Hand Operated</td>\n</tr>\n<tr>\n<td width=\"186\">Recommended Use</td>\n<td width=\"30\"></td>\n<td width=\"329\">Water-based media, detergents, soaps, antifreeze, windshield washer, hydraulic oils, lubricants, herbicides &amp; pesticides, adblue, urea, DEF and pump should only be used with non-flammable liquids</td>\n</tr>\n<tr>\n<td width=\"186\"><strong>Do Not Use With </strong></td>\n<td width=\"30\"></td>\n<td width=\"329\">Do not use with any media not compatible with materials used in the pump construction, these pumps must never be used for fuel transfer or with thinners, solvents etc\u2026</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Plastic-Lever-Pump2.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Plastic-Lever-Pump2.jpg 960w, https://www.kijeka.com/wp-content/uploads/2017/06/Plastic-Lever-Pump2-115x300.jpg 115w, https://www.kijeka.com/wp-content/uploads/2017/06/Plastic-Lever-Pump2-768x2008.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Plastic-Lever-Pump2-392x1024.jpg 392w, https://www.kijeka.com/wp-content/uploads/2017/06/Plastic-Lever-Pump2-34x90.jpg 34w, https://www.kijeka.com/wp-content/uploads/2017/06/Plastic-Lever-Pump2-134x350.jpg 134w, https://www.kijeka.com/wp-content/uploads/2017/06/Plastic-Lever-Pump2-184x480.jpg 184w, https://www.kijeka.com/wp-content/uploads/2017/06/Plastic-Lever-Pump2-270x706.jpg 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Plastic-Lever-Pump-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Plastic-Lever-Pump-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Plastic-Lever-Pump-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/polyethylene-siphon-pumps/",
                "name": "Polyethylene Siphon Pumps",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Siphon pumps are easy to prime &amp; start liquid within 6-7 Strokes, Pump requires no further operation &amp; Keep working in Auto Position</li>\n<li>Siphon pumps are equipped with a vent cap on top. Operating the cap stops discharge.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"545\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"329\"><strong>Polyethylene Siphon Pump.</strong></td>\n</tr>\n<tr>\n<td width=\"186\">Wetted\u00a0 Components</td>\n<td width=\"30\"></td>\n<td width=\"329\">Polyethylene &amp; PVC</td>\n</tr>\n<tr>\n<td width=\"186\">Drive Type</td>\n<td width=\"30\"></td>\n<td width=\"329\">\u00a0\u00a0\u00a0 Manual/ Hand Operated</td>\n</tr>\n<tr>\n<td width=\"186\">Recommended Use</td>\n<td width=\"30\"></td>\n<td width=\"329\">Water-based media, detergents, soaps, some mild acids &amp; Other liquid which Compatible with pump construction Material. Pump Should only be used with light weight &amp; Non-flammable liquids</td>\n</tr>\n<tr>\n<td width=\"186\"><strong>Do Not Use With </strong></td>\n<td width=\"30\"></td>\n<td width=\"329\">Any Media that is not compatible with materials used in the pump construction</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Polyethylene-Siphon-Pumps-scaled.jpg"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/polypropylene-rotary-barrel-pump/",
                "name": "Polypropylene Rotary Barrel Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Lightweight rotary pumps are manufactured using the highest quality engineered plastics to provide superior chemical resistance.</li>\n<li>pump body is made from glass filled polypropylene with Ryton veins</li>\n<li>seals are from Viton rubber &amp; all pump hardware is stainless steel</li>\n<li>Complete with 3 Pc threaded polypropylene suction tube &amp; a choice of two 2\u2033 Bung adaptors.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td>\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td><strong>Polypropylene Rotary Barrel Pump.</strong></td>\n</tr>\n<tr>\n<td>Wetted\u00a0 Components</td>\n<td>Polypropylene, Ryton, Viton &amp; Stainless Steel</td>\n</tr>\n<tr>\n<td>Drive Type</td>\n<td>\u00a0 Manual/ Hand Operated</td>\n</tr>\n<tr>\n<td>Recommended Use</td>\n<td>Water Based Media, Acids, Chemicals, Detergents, Benzene, Glycerine Etc\u2026</td>\n</tr>\n<tr>\n<td><strong>Do Not Use With </strong></td>\n<td>Acetone, Lacquer, Mineral Oils, Solvents,\u00a0\u00a0\u00a0 Turpentine Etc.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Polypropylene-Rotary-Drun-Pump-1-scaled.jpg"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/ss-corrugated-flexible-hoses/",
                "name": "SS Corrugated Flexible Hoses",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<p>Stainless steel annular corrugated metallic flexible hoses are manufacturing in steel ANSI 321, 316, 316L &amp; 304 grades conforming to BS 6501, Part-1 : 2004 / ISO 10380 : 2012. The annular corrugated metallic hose body provided the flexibility and pressure tight core of the assembly. \u00a0Stainless steel annular corrugated metallic flexible hose are offered from Size: 1/4\u2033(DN 6) to 12\u2033(DN 300).</p>\n<p>\u00a0</p>\n<table width=\"553\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"224\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"329\"><strong>SS Corrugated Flexible Hoses.</strong></td>\n</tr>\n<tr>\n<td width=\"186\">Available Sizes</td>\n<td width=\"38\"></td>\n<td width=\"329\">\u00bc\u201d to 12\u201d Diameter</td>\n</tr>\n<tr>\n<td width=\"186\">Length</td>\n<td width=\"38\">Meter</td>\n<td width=\"329\">As Per requirement</td>\n</tr>\n<tr>\n<td width=\"186\">Available MOC</td>\n<td width=\"38\"></td>\n<td width=\"329\">SS 304, SS 316, SS 316L Single or Double wire braid Flexible Hose \u00a0With SS Or Teflon inner Corrugation</td>\n</tr>\n<tr>\n<td width=\"186\">SS Hose Advantage</td>\n<td width=\"38\"></td>\n<td width=\"329\">\u00b7\u00a0\u00a0\u00a0\u00a0\u00a0 High physical strength combined with light weight.\n<p>\u00b7\u00a0\u00a0\u00a0\u00a0\u00a0 Suitable for wide temperature range (-270oC to 700oC), Good corrosion resistance,</p>\n<p>\u00b7\u00a0\u00a0\u00a0\u00a0\u00a0 Resistance to fire, moisture, abrasion &amp; penetration.</p>\n<p>\u00b7\u00a0\u00a0\u00a0\u00a0\u00a0 Absorbs vibration and noise from pumps, compressors, engines etc.</p>\n<p>\u00b7\u00a0\u00a0\u00a0\u00a0\u00a0 Compensates for thermal expansion or contraction of piping.</p>\n<p>\u00b7\u00a0\u00a0\u00a0\u00a0\u00a0 Correct problems of misalignment.</p>\n<p>\u00b7\u00a0\u00a0\u00a0\u00a0\u00a0 A flexible &amp; quick alternative for rigid piping in difficult locations.</p>\n<p>\u00a0</p></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses.png 553w, https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses-300x114.png 300w, https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses-270x103.png 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses.3-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses.3-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses.3-170x170.png 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses.2-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses.2-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses.2-170x170.png 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses.1-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses.1-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses.1-170x170.png 170w, https://www.kijeka.com/wp-content/uploads/2017/06/SS-Corrugated-Flexible-Hoses.1.png 207w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/stainless-steel-316-electric-ibc-container-pump/",
                "name": "Stainless Steel 316 Electric IBC Container Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>IBC Container Pumps, the customer focused and user friendly, handles a wide range of chemicals from Caustic to severe Oils, Lubricants, Solvents, Fragrances, Flavours and Essential Oils.</li>\n<li><strong>Working Principle</strong> The pump tube is connected to motor by means of self \u2013 aligning coupling. The motor transmits power through coupling to the drive shaft of pump which is well supported By Teflon bearing. The impeller is mounted at the foot piece of the pump tube and is always immersed in the liquid which assures self-priming.</li>\n</ul>\n<p><u>\u00a0</u></p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Low Viscous Liquid Transfer from the IBC Container</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td colspan=\"2\" style=\"text-align: center;\" width=\"198\"><strong>Model</strong></td>\n<td width=\"324\"><strong>Stainless Steel 316 Electric IBC Container Pump.</strong></td>\n</tr>\n<tr>\n<td width=\"102\">Pump MOC</td>\n<td width=\"96\"></td>\n<td width=\"324\">SS 316</td>\n</tr>\n<tr>\n<td width=\"102\">Drive Type</td>\n<td width=\"96\"></td>\n<td width=\"324\">Electric Motor ( Detachable)</td>\n</tr>\n<tr>\n<td width=\"102\">Drive Option</td>\n<td width=\"96\"></td>\n<td width=\"324\">Flameproof Electric &amp; Non- Flameproof</td>\n</tr>\n<tr>\n<td width=\"102\">Capacity</td>\n<td width=\"96\">Litre/Min.</td>\n<td width=\"324\">Maximum 150</td>\n</tr>\n<tr>\n<td width=\"102\">Head</td>\n<td width=\"96\">Meter</td>\n<td width=\"324\">Maximum 7 Meter</td>\n</tr>\n<tr>\n<td width=\"102\">Suction Diameter</td>\n<td width=\"96\">mm</td>\n<td width=\"324\">5\u201d At Bottom</td>\n</tr>\n<tr>\n<td width=\"102\">Suction Tube\n<p>Length</p></td>\n<td width=\"96\">mm</td>\n<td width=\"324\">1200 mm</td>\n</tr>\n<tr>\n<td width=\"102\">Discharge Size</td>\n<td width=\"96\">mm</td>\n<td width=\"324\">40 mmsuitable for 1\u2033 Hose.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Stainless-Steel-316-Electric-IBC-Container-Pump.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/stainless-steel-air-operated-piston-drum-pump/",
                "name": "Stainless Steel Air Operated Piston Drum Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>S. 316 Lift-action, Piston type Non-sparking /flameproof Pneumatic drum pumps</li>\n</ul>\n<ul>\n<li><strong>This pump would generate Discharge Pressure equivalent to Supply Air Pressure. </strong></li>\n<li>There is no damage for any part if the Pump <strong>RUNS DRY</strong>.</li>\n<li>You can easily shut off the pump by just shut down the discharge valve at Operation Area.</li>\n</ul>\n<ul>\n<li>Barrel pumps for quickly and easily dispenses Low <strong>Viscous </strong>from all 210 Liters</li>\n<li>For Any Solvents and Chemicals compatible with SS 316 and PTFE</li>\n</ul>\n<p><u>\u00a0</u></p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Low Viscous Liquid Transfer from the Drum/ Barrel</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"545\">\n<tbody>\n<tr>\n<td colspan=\"2\" style=\"text-align: center;\" width=\"227\"><strong>Model</strong></td>\n<td width=\"318\"><strong>Stainless Steel Air Operated Piston Drum Pump.</strong></td>\n</tr>\n<tr>\n<td width=\"186\">Pump MOC</td>\n<td width=\"41\"></td>\n<td width=\"318\">SS 316 &amp; TEFLON</td>\n</tr>\n<tr>\n<td width=\"186\">Drive Type</td>\n<td width=\"41\"></td>\n<td width=\"318\">Pneumatic / Air Operated</td>\n</tr>\n<tr>\n<td width=\"186\"><strong>Air Consumption</strong></td>\n<td width=\"41\">CFM</td>\n<td width=\"318\">12 CFM</td>\n</tr>\n<tr>\n<td width=\"186\"><strong>Required Air Pressure</strong></td>\n<td width=\"41\">Bar</td>\n<td width=\"318\">3-6 Bar</td>\n</tr>\n<tr>\n<td width=\"186\">Suction Length</td>\n<td width=\"41\">mm</td>\n<td width=\"318\">920 mm</td>\n</tr>\n<tr>\n<td width=\"186\">Suction Pipe</td>\n<td width=\"41\">mm</td>\n<td width=\"318\">44 mm</td>\n</tr>\n<tr>\n<td width=\"186\">Discharge Size</td>\n<td width=\"41\">mm</td>\n<td width=\"318\">\u00a0\u00be\u201d Serrated Nozzle</td>\n</tr>\n<tr>\n<td width=\"186\">Pump Seals</td>\n<td width=\"41\"></td>\n<td width=\"318\">\u00a0\u00a0 PTFE ( Teflon)</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Stainless-Steel-Air-Operated-Piston-Drum-Pump.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/stainless-steel-piston-type-drum-pump/",
                "name": "Stainless Steel Piston Type Drum Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>S. 316 Lift-action, Piston type Non-sparking /flameproof hand operated drum pumps</li>\n<li>Barrel pumps for quickly and easily dispenses Low <strong>Viscous </strong>from all 210 Liters</li>\n<li>For Any Solvents and Chemicals compatible with SS 316 and PTFE.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Low Viscous Liquid Transfer from the Drum/ Barrel</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"427\">\n<tbody>\n<tr>\n<td colspan=\"2\" style=\"text-align: center;\" width=\"161\"><strong>Model</strong></td>\n<td width=\"266\"><strong>SS 316 Piston Type Drum Pump</strong></td>\n</tr>\n<tr>\n<td width=\"126\">Pump MOC</td>\n<td width=\"35\"></td>\n<td width=\"266\">SS 316 &amp; TEFLON</td>\n</tr>\n<tr>\n<td width=\"126\">Drive Type</td>\n<td width=\"35\"></td>\n<td width=\"266\">Manual/ Hand Operated</td>\n</tr>\n<tr>\n<td width=\"126\">Suction Length</td>\n<td width=\"35\">mm</td>\n<td width=\"266\">1000 mm</td>\n</tr>\n<tr>\n<td width=\"126\">Suction Pipe</td>\n<td width=\"35\">mm</td>\n<td width=\"266\">38 mm</td>\n</tr>\n<tr>\n<td width=\"126\">Discharge Size</td>\n<td width=\"35\">mm</td>\n<td width=\"266\">20 mm</td>\n</tr>\n<tr>\n<td width=\"126\">Pump Seals</td>\n<td width=\"35\"></td>\n<td width=\"266\">\u00a0PTFE ( Teflon)</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/SS-316-Piston-Drum-Pump-scaled.jpg"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/stainless-steel-rotary-drum-pump/",
                "name": "Stainless Steel Rotary Drum Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Rotary action Non-sparking / flameproof hand Operated drum pumps</li>\n<li>Self-priming barrel pump quickly &amp; easily dispenses corrosive Liquids/chemicals</li>\n<li>Barrel pumps made exclusively from Teflon and stainless steel Materials.</li>\n<li>For Any Solvents and Low Viscous Chemicals which are compatible With</li>\n</ul>\n<p>Stainless Steel &amp; Teflon (PTFE)</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Low Viscous Liquid Transfer from the Drum/ Barrel</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"664\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"161\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"266\"><strong>SS 316 Rotary Drum Pump.</strong></td>\n<td width=\"237\"><strong>SS 304 Rotary Drum Pump.</strong></td>\n</tr>\n<tr>\n<td width=\"126\">Pump MOC</td>\n<td width=\"35\"></td>\n<td width=\"266\">SS 316 &amp; TEFLON</td>\n<td width=\"237\">SS 304\u00a0 &amp; TEFLON</td>\n</tr>\n<tr>\n<td width=\"126\">Drive Type</td>\n<td width=\"35\"></td>\n<td width=\"266\">Manual/ Hand Operated</td>\n<td width=\"237\">Manual/ Hand Operated</td>\n</tr>\n<tr>\n<td width=\"126\">Head</td>\n<td width=\"35\">Meter</td>\n<td width=\"266\">Maximum 4 Meter</td>\n<td width=\"237\">Maximum 4 Meter</td>\n</tr>\n<tr>\n<td width=\"126\">Suction Tube Length</td>\n<td width=\"35\">mm</td>\n<td width=\"266\">1000 mm</td>\n<td width=\"237\">1000 mm</td>\n</tr>\n<tr>\n<td width=\"126\">Suction &amp; Delivery Pipe</td>\n<td width=\"35\">mm</td>\n<td width=\"266\">1\u201d OD SS 316 Pipe</td>\n<td width=\"237\">1\u201d OD SS 316 Pipe</td>\n</tr>\n<tr>\n<td width=\"126\">Operating Handle</td>\n<td width=\"35\">mm</td>\n<td width=\"266\">SS 316 Quality Material</td>\n<td width=\"237\">SS 316 Quality Material</td>\n</tr>\n<tr>\n<td width=\"126\">Pump Seal&amp; Blade</td>\n<td width=\"35\"></td>\n<td width=\"266\">PTFE ( Teflon)</td>\n<td width=\"237\">PTFE ( Teflon)</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/SS-Rotary-Drum-Pumps-scaled.jpg"
                    ]
                ]
            }
        ],
        "Cranes & Lifting Accessories": [
            {
                "link": "https://www.kijeka.com/product/chain-hoist/",
                "name": "Chain Hoist",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>The manual chain hoist is portable lifting device easily operated by hand chain.</li>\n<li>It is suitable for use in garages, workshops and warehouses for loading and unloading goods.</li>\n<li>It is specially advantageous for lifting work in open air grounds and places where no power supply is available.</li>\n<li>The chain hoist can be attached to a trolley as a travelling chain hoist. It is suitable to monorail overhead conveying system, hand travelling crane and jib crane.</li>\n<li>Manual Chain hoist for loading or lifting of dies, engines, heavy Plates, machines, equipment\u2019s etc\u2026</li>\n<li>Durable hardened steel construction.</li>\n<li>Drop forged, heat treated steel safety latch hooks.</li>\n<li>Designed to provide safe, easy and efficient lifting operations.</li>\n<li>Made of high quality steel for industrial applications.</li>\n<li>Lifts load: From 0 to 20 meters.</li>\n<li><strong>Available capacity: From 500 Kgs to 10,000 Kgs.</strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Chain-Hoist.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Chain-Hoist.png 205w, https://www.kijeka.com/wp-content/uploads/2017/12/Chain-Hoist-82x300.png 82w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/electric-wire-rope-hoist/",
                "name": "Electric Wire Rope Hoist",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>We are engaged in offering a wide array of Wire Rope Electric Hoists to our customers.</li>\n<li>These products are used to lift bulky and heavy material. Our range of products is easy to install and is highly appreciated for its sturdy construction, compact design, noiseless operation and easy maintenance.</li>\n<li><strong>Available capacity: From 500 Kgs to 5000 Kgs.</strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Electric-Wire-Rope-Hoist.-KE308E.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Electric-Wire-Rope-Hoist.-KE308E.jpg 437w, https://www.kijeka.com/wp-content/uploads/2017/12/Electric-Wire-Rope-Hoist.-KE308E-269x300.jpg 269w, https://www.kijeka.com/wp-content/uploads/2017/12/Electric-Wire-Rope-Hoist.-KE308E-70x78.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/12/Electric-Wire-Rope-Hoist.-KE308E-270x301.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/12/Electric-Wire-Rope-Hoist.-KE308E-370x412.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/eot-crane/",
                "name": "EOT Crane",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>We are instrumental in manufacturing, supplying and exporting an extensive range of Single/ Double Girder Electric Crane.</strong></li>\n<li>Our products are designed and manufactured under the guidance of dexterous professionals in accordance to ISO 3177 standards, thus meeting clients\u2019 varying needs. Owing to attributes like efficiency, longer serviceability and robust construction, these products are widely appreciated by the customers.</li>\n<li>Single Girder Overhead Cranes Capacity Range : 1.0 Ton to 20 Ton</li>\n<li>Double Girder Overhead Cranes Capacity Range : 1.0 Ton to 150 Ton</li>\n<li>Span Range : 3 meters to 36 meters</li>\n<li><strong>EOT Cranes are available in the entire range of duty and class of capacities, from 1-150 tones </strong><br/>\n<strong>and within a span to suit your specific requirement.</strong></li>\n<li>Class I : Light duty cranes for repair shops, light assembly operations, service buildings, light<br/>\nwarehouses, where service requirements are infrequent.</li>\n<li>Class II : Medium duty cranes for machine shops and general industrial use both indoor and outdoor<br/>\napplication.</li>\n<li>Class III : Extra heavy duty cranes for steel mills and other heavy machine shops, steel warehouses,<br/>\nheavy fabrication shops, paper mills etc. with magnet and bucket operation for scrap yards, fertilizer<br/>\nplants &amp; induction furnace.</li>\n<li>Class IV : Extra heavy duty cranes for steel mills and other heavy engineering purposes. Cranes<br/>\ndesigned for hot metal application on request.</li>\n<li><strong>Structure :</strong> Bridge Girder, End carriages, Crab Frame manufactured from box plate design / Rolled<br/>\nSections. If required 100% radiography of all butt welding joints of bridge and end carriages can be<br/>\nprovided. The material of construction conforms to IS:2062, and the bridge is designed for minimum<br/>\nvibration.</li>\n<li><strong>Wheel Assemblies :</strong> Trolley and crane wheels are straight treaded double flanged forged steel EN 9,<br/>\nheat treated to achieve a special <em>sorbitized </em>structure up to a depth of 15-20 mm from the surface and<br/>\ngradually diminishing towards the Centre retaining the Core Properties. These wheels are<br/>\nsupported on antifriction ball/roller bearings, in special L-type bearing blocks. Wheels also available of<br/>\ngear and pinion type.</li>\n<li><strong>Gearing :</strong> The gear reducers are constructed either in double, triple and quadruple reduction using<br/>\nrugged wide faced helical and spur gears that are precision cut from special alloy steel forgings. And to<br/>\nprotect the gear train from shock loads, all gears and\u00a0 are supported between two antifriction<br/>\nball/roller bearings. All gear units are totally enclosed with oil bath splash lubrication.</li>\n<li><strong>Crane micro drive special gear boxes :</strong> The special micro drive provides fine inching<br/>\nmovements of hoist, trolley or crane at the rate of 5% to 20% of the main speed. The micro drive is<br/>\nachieved by a separate gear box, with unique sun and planet system. Gearing system fitted on the<br/>\ninput side of main gear unit and pony motor with separate brake unit. It is a positive drive and avoids<br/>\nthe use of clutches etc.</li>\n<li><strong>Cranes Drives :</strong> We offer a wide selection of A.C. control packages to meet your electrical<br/>\nrequirements. We select only the best standard crane and hoist duty motors and all electrical<br/>\ncomponents and accessories from the nation\u2019s leading manufacturers to ensure dependable driving<br/>\npower.</li>\n<li><strong>Variable Frequency Drives &amp; Remote Controls :</strong> We also offer Variable Frequency Drive in hoisting,<br/>\ncross travel, long travel for step less speed control as an optional feature. We also provide radio<br/>\nremote control cranes for application in inaccessible and hazardous areas.</li>\n<li><strong>Brakes :</strong> Failsafe magnetic or hydraulic brakes of 150% torque or more are fitted on shaft extensions.<br/>\nFor heavy duty cranes a second brake can be mounted to ensure failsafe operation.</li>\n<li><strong>Controls :</strong> Pendant control from floor, master control switches, master controllers in the driver\u2019s cabin<br/>\ncan be provided. Radio remote control can be provided on request.<br/>\n<strong>Cabin :</strong> Open or enclosed type driver\u2019s cabin available. The cabins can be provided either at one end<br/>\nof the bridge girder or center of bridge girder. Moving type cabin fitted with crab can also be provided.<br/>\nEnclosed cabin is well ventilated, Standard Cabin accessories are operating switches, protective panel, and safe ladder from platform. Driver\u2019s seat, Exhaust fan, Insulated floor matting, Fire extinguishers are provided on request.</li>\n</ul>\n<div id=\"masterdiv\">\n<div class=\"switchgroup1\" id=\"bobcontent1\"></div>\n</div>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/EOT-Crane.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/EOT-Crane.jpg 1350w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT-Crane-300x185.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT-Crane-1024x630.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT-Crane-768x473.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT-Crane-70x43.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT-Crane-270x166.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT-Crane-370x228.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT-Crane-1170x720.jpg 1170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/EOT-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/EOT-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/EOT2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/EOT2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT2-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT2-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT2-270x270.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT2-370x370.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT2-170x170.jpg 170w, https://www.kijeka.com/wp-content/uploads/2021/04/EOT2.jpg 730w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/extendable-forklift-jib/",
                "name": "Extendable Forklift Jib",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Similar concept to the standard Low Profile Jib, however the extensions allow greater flexibility, allowing the maneuvering of long and awkward loads from inaccessible locations</strong></li>\n<li>Includes 2 hooks and shackles to enable you to \u2018cradle\u2019 your load.</li>\n<li>Multi Hook positioner.</li>\n<li>Four-way\u00a0pocket entry for ease of storage</li>\n<li>Supplied complete with swivel hook and bow shackles</li>\n<li>Zinc plated heel pins for safe attachment to the forklift truck</li>\n<li>Duly Paint or Powder Coated finish</li>\n<li>Available ranging from 1000kg to 3000 kg lifting capacity.</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Low-Profile-Extending.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Low-Profile-Extending.jpg 800w, https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Low-Profile-Extending-300x131.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Low-Profile-Extending-768x334.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Low-Profile-Extending-70x30.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Low-Profile-Extending-270x117.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Low-Profile-Extending-370x161.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/forklift-coil-rams-lifters/",
                "name": "Forklift Coil Rams & Lifters",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Fork mounted coil rams are used to pick up slit coils and master coils and place them in coil racks.</strong></li>\n<li>These forklift attachments for lifting can be used to easily lift and carry many types of coiled material. Unless you have an overhead crane coil rams for forklifts are a necessity if you are handling and storing coils.</li>\n<li>Forklift coil lifters come in a variety of sizes and capacities.</li>\n<li>Lengths from 24\u2033 to 48\u2033 and capacities from 500 to 2500 kgs</li>\n<li>The coil ram &amp; lifter can be ordered with either a 4-1/2\u2033 or 5-9/16\u2033 diameter ram poles.</li>\n<li>The carriage mounted rug rams have a spring loaded locking pin to secure it to the carriage.</li>\n<li>All models are constructed of steel and have a high quality blue powder coat paint finish.</li>\n<li><strong>Available ranging from 1000kg to 3000 kg lifting capacity.</strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/coil_r84.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/coil_r84.jpg 400w, https://www.kijeka.com/wp-content/uploads/2021/04/coil_r84-300x236.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/coil_r84-70x55.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/coil_r84-270x213.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/coil_r84-370x291.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/forklift-fork-extensions/",
                "name": "Forklift Fork Extensions",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Ideal for safe and stable handling of loads which are longer than the forklift forks, our fork extensions offer long reach and stabilizing capabilities, whilst retaining the maneuverability of the lift truck for conventional operating.</li>\n<li>Manufactured from heavy duty 5mm thick steel with additional 10 mm thick internal strengthening plates, all our fork extensions incorporate a fully rounded toe, with heavy duty capping, for easy entry into and out of loads or pallets.</li>\n<li>A removable heel pin allows for drive in entry, negating the need for manual lifting (in compliance with Health &amp; Safety manual lifting regulations), whilst ensuring the ork extensions are safely secured to the truck forks.</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/heavy-duty-fork-extensions.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/heavy-duty-fork-extensions.jpg 783w, https://www.kijeka.com/wp-content/uploads/2021/04/heavy-duty-fork-extensions-300x182.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/heavy-duty-fork-extensions-768x467.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/heavy-duty-fork-extensions-70x43.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/heavy-duty-fork-extensions-270x164.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/heavy-duty-fork-extensions-370x225.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/forklift-hook-attachement/",
                "name": "Forklift Hook Attachement",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Our adjustable forklift hook attachment is a simple and cost effective way of safely hanging a load under the forks.</strong></li>\n<li>The forklift hook can be adjusted to suit a position anywhere along the length of the forklift fork, therefore giving you more flexibility when it comes to handling loads of different sizes or where there are different reach requirements.</li>\n<li>To safely ensure the forklift hook is retained to the forks, the unit is supplied with two large \u2018T\u2019 screws. That will allow the hook to be tightened to the fork from the underside.</li>\n<li>The forklift hook comes supplied with a high quality hook and shackle, and like all our forklift attachments</li>\n<li><strong>Available Capacity :</strong> 1000Kgs to 5000kgs.</li>\n<li>Fork Pocket Size: 140x50mm to 150x80mm</li>\n<li>Fork Spread: 676mm &amp;\u00a0 794mm</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/adjustable-forklift-hook.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/adjustable-forklift-hook.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2020/05/adjustable-forklift-hook-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2020/05/adjustable-forklift-hook-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2020/05/adjustable-forklift-hook-768x768.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/adjustable-forklift-hook-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/adjustable-forklift-hook-270x270.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/adjustable-forklift-hook-370x370.jpg 370w, https://www.kijeka.com/wp-content/uploads/2020/05/adjustable-forklift-hook-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/forklift-mounted-battery-lifting-beam/",
                "name": "Forklift Mounted Battery Lifting Beam",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Application:</strong>\n<ul>\n<li>The battery handling beam offers a heavy duty non-conductive method of lifting batteries.</li>\n<li>The non-slip hook design fits snugly into most battery lifting holes.</li>\n<li><strong>For Handling, Lifting of Industrial Heavy Duty Batteries\u00a0</strong></li>\n</ul>\n</li>\n</ul>\n<table width=\"0\">\n<thead>\n<tr>\n<td><strong>Capacity (kg)</strong></td>\n<td><strong>Lifting Point Centers (mm)</strong></td>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>1000</td>\n<td>900\u00d7570 (outer)</td>\n</tr>\n<tr>\n<td>2000</td>\n<td>900\u00d7570 (outer)</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Forklift-Battery-Lift-Beam.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Forklift-Battery-Lift-Beam.jpg 366w, https://www.kijeka.com/wp-content/uploads/2021/04/Forklift-Battery-Lift-Beam-214x300.jpg 214w, https://www.kijeka.com/wp-content/uploads/2021/04/Forklift-Battery-Lift-Beam-64x90.jpg 64w, https://www.kijeka.com/wp-content/uploads/2021/04/Forklift-Battery-Lift-Beam-250x350.jpg 250w, https://www.kijeka.com/wp-content/uploads/2021/04/Forklift-Battery-Lift-Beam-342x480.jpg 342w, https://www.kijeka.com/wp-content/uploads/2021/04/Forklift-Battery-Lift-Beam-270x378.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/gear-trolley/",
                "name": "Gear Trolley",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Geared trolley used for easy push- pull movement of chin hoist.</strong></li>\n<li>Available for different \u201cI\u201d sections beams.</li>\n<li>Machined steel wheels, mounted on pre-lubricated encapsulated ball bearings.</li>\n<li><strong>Available capacity: From 500 Kgs to 10,000 Kgs.</strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Gear-Trolley.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Gear-Trolley.png 593w, https://www.kijeka.com/wp-content/uploads/2017/12/Gear-Trolley-300x280.png 300w, https://www.kijeka.com/wp-content/uploads/2017/12/Gear-Trolley-270x252.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/jib-crane/",
                "name": "Jib Crane",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>We are offering our clients a wide range of JIB Cranes Like Base Plate Mounted, Insert Mounted &amp; Sleeve Insert Mounted, Wall mounted etc..</li>\n<li>All Types of the free Standing Series use a Similar Mast Pipe, Head Assembly &amp; I-Beam Boom</li>\n<li>Jib Crane is use in various applications such as material loading &amp; unloading, heavy machine loading and light assembly work</li>\n<li>Different In Model is found in the Mounting arrangement provide for 360 Degree Of Continuous Rotation</li>\n<li>Jib Crane manufactured by our professionals, using superior quality raw material in accordance to international quality standards.</li>\n<li>Due to their robust construction, durability and excellent performance, these products are highly appreciated and demanded among the customers.</li>\n<li><strong>Capacity Range : 500Kgs to 5000 Kgs</strong></li>\n<li><strong>Note:\u00a0</strong>Jib\u00a0 Crane is Customized Product, for More details, <em><b>Kindly email\u00a0 us Required Capacity, Lifting Height &amp; also Describe your application\u00a0</b></em><em>\u00a0</em></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Crane.-KE-JIBC-2.png",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Crane.-KE-JIBC-2.png 1260w, https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Crane.-KE-JIBC-2-275x300.png 275w, https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Crane.-KE-JIBC-2-938x1024.png 938w, https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Crane.-KE-JIBC-2-768x838.png 768w, https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Crane.-KE-JIBC-2-70x76.png 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Crane.-KE-JIBC-2-270x295.png 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Crane.-KE-JIBC-2-370x404.png 370w, https://www.kijeka.com/wp-content/uploads/2021/04/Jib-Crane.-KE-JIBC-2-1170x1277.png 1170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Crane-useage-Types-copy-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Crane-useage-Types-copy-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Crane-useage-Types-copy-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-2-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-2-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-2-270x270.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-2-370x370.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-2-170x170.jpg 170w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-2.jpg 730w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Swing-Arm-Crane-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Swing-Arm-Crane-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Swing-Arm-Crane-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Swing-Arm-Crane-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Swing-Arm-Crane-270x270.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Swing-Arm-Crane-370x370.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/Swing-Arm-Crane-170x170.jpg 170w, https://www.kijeka.com/wp-content/uploads/2021/04/Swing-Arm-Crane.jpg 380w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Crane-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Crane-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Crane-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-270x270.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-370x370.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane-170x170.jpg 170w, https://www.kijeka.com/wp-content/uploads/2021/04/Wall-Mounted-Slewing-Light-crane.jpg 730w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/lifting-tackles-slings-wire-rope/",
                "name": "Lifting Tackles, Slings, Wire Rope",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>We are engaged in offering a wide array of\u00a0 Lifting Tackles, including Polyester Webbing Slings, Round Endless Slings, Ratchet, Cargo Lashing, Wire Rope, Wire Rope Sling, Chain Sling, Lifting Tackles, Pulling Lifting Machine, Ratchet Lever Hoist, Plate Lifting Clamps, Load Binder, Lashing Winch, Plate Buckle, Ratchet Hook, Special Lashing Hooks.. Etc..</li>\n<li><strong>Webbing Polyester Slings: </strong>Available Capacity : 1 Ton to 24 Ton</li>\n</ul>\n<p>For Order Kindly Provide Required: Width X Capacity x Effective Length in Meter</p>\n<ul>\n<li><strong>Round Endless Polyester Slings: </strong>Available Capacity : 1 Ton to 30 Ton</li>\n<li><strong>Flat Endless Polyester Slings: </strong>Available Capacity:\u00a0 1 Ton to 12 Ton</li>\n<li><strong>Eye and Eye Polyester Slings: </strong>Available Capacity : 1 Ton to 12 Ton</li>\n<li><strong>Ratchet Lashing : Endless Type Or Two Part </strong></li>\n<li><strong>Polyester Multileg Slings: </strong>we design and supply polyester multileg slings made from quality webbing/round slings with desired end fittings like O Ring/Oblong Ring at top And Hooks/D shackles/Bow shackles at bottom.</li>\n<li><strong>Wire Rope: </strong>Available with different diameters &amp; Capacity across wide variety of constructions used in general engineering, mining, shipping, fishing, elevators, oil drilling, aerial rope, locked coiled ropes</li>\n<li><strong>Wire Rope Slings: 1. Single Part Slings</strong> with different Type of End like Eye &amp; Eye, Eye &amp; Thimble, Thimble &amp; Thimble, Eye &amp; D-Shackle, Thimble &amp; D-Shackle, Eye &amp; Eye Hook, Thimble &amp; Eye Hook, Eye &amp; Swivel Hook, Thimble &amp; Swivel Hook <strong>2</strong>. <strong>Multi Leg Wire Rope Slings </strong><strong>available in two legged, three legged and four legged combination with different types of end fittings</strong></li>\n<li><strong>Chain &amp; Chain Slings: </strong>Available in different sizes &amp; Various end fittings possible, Manufactured as per IS specifications and grade 30/63/80 &amp; above</li>\n<li><strong>Plate Lifting Clamps: </strong>Plate Lifting Clamps are generally manufactured in pairs. The Grips of the Clamp is made out of hardened steel which prevents the clamp from slipping the off load. The Clamps can be supplied either with serrated teeth or smooth faced which-ever preferred by the Buyer.</li>\n<li><strong>Adjustable Bridle / Multileg Slings: </strong>These are normally used for lifting non uniform loads where the load is imbalanced due to non-uniformity of mass. This is so designed that the legs are adjusted and the center of gravity is lined up for balanced handling of Non-uniform loads</li>\n<li><strong>Drum Lifting Belt:</strong> Drum Lifting Belt Available for Steel Drum- Horizontal Or Vertical Lifting Purpose</li>\n<li><strong>Cargo Nets: </strong>We Supply cargo nets of different specifications and sizes as per customers\u00a0 requirement</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Lifting-Tackles-Slings-Wire-Rope.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Lifting-Tackles-Slings-Wire-Rope.png 606w, https://www.kijeka.com/wp-content/uploads/2017/12/Lifting-Tackles-Slings-Wire-Rope-213x300.png 213w, https://www.kijeka.com/wp-content/uploads/2017/12/Lifting-Tackles-Slings-Wire-Rope-270x381.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/low-profile-forklift-jib/",
                "name": "Low Profile Forklift Jib",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Kijeka Low profile jib allows the movement of long and awkward loads from inaccessible locations, with the potential for 5 different lifting centers</strong>.</li>\n<li>Multi-hook positioning from 500-1750mm centers</li>\n<li>Supplied complete with swivel hook and bow shackles</li>\n<li>Four-way\u00a0pocket entry for ease of storage</li>\n<li>Zinc plated heel pins for safe attachment to the forklift truck</li>\n<li>Duly Paint or Powder Coated finish</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Forklift-JIB.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Forklift-JIB.jpg 500w, https://www.kijeka.com/wp-content/uploads/2021/04/Forklift-JIB-300x130.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Forklift-JIB-70x30.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Forklift-JIB-270x117.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Forklift-JIB-370x161.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/mobile-floor-cranes/",
                "name": "Mobile Floor Crane",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Mobile floor crane serves as the most simplest and financial answer for completing your lifting and bringing down issues.</li>\n<li>Designed for heavy-duty lifting, loading and positioning.</li>\n<li>Ruggedly-constructed; will give dependable, long-lasting use Standard</li>\n<li>Hand pump hydraulic lift cylinder.</li>\n</ul>\n<p><strong>\u00a0</strong></p>\n<table width=\"427\">\n<tbody>\n<tr>\n<td width=\"163\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"265\"><strong>Mobile Floor Crane</strong></td>\n</tr>\n<tr>\n<td width=\"163\">MOC</td>\n<td width=\"265\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"163\">Drive Type</td>\n<td width=\"265\">Manual Push-Pull Type &amp;\u00a0 Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"163\">Minimum Hook Height</td>\n<td width=\"265\">500 mm</td>\n</tr>\n<tr>\n<td width=\"163\">Maximum Hook Height</td>\n<td width=\"265\">3100mm to 5000mm</td>\n</tr>\n<tr>\n<td width=\"163\">Available Option</td>\n<td width=\"265\">Hydraulic- Manual , Electric Operated, Battery\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 Operated</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Mobile-Floor-Cranes.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Mobile-Floor-Cranes.png 523w, https://www.kijeka.com/wp-content/uploads/2017/12/Mobile-Floor-Cranes-271x300.png 271w, https://www.kijeka.com/wp-content/uploads/2017/12/Mobile-Floor-Cranes-270x299.png 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Mobile-Floor-Cranes2-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Mobile-Floor-Cranes2-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/12/Mobile-Floor-Cranes2-170x170.png 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Mobile-Floor-Cranes3-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Mobile-Floor-Cranes3-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/12/Mobile-Floor-Cranes3-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/portable-gantry-crane/",
                "name": "Portable Gantry Crane",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Gantry Cranes are straightforward, durable, and dependable lifting solutions.</li>\n<li>Our gantry hoist is available in capacities up to 5 ton and spans up to 30 feet.</li>\n<li>Square tubing uprights, knee braces, and channel base provide for stable lifting and movement</li>\n<li>Bolted beam to upright connection ensures safety</li>\n<li>Movable with Casters having Solid Rubber wheels</li>\n<li><strong>Capacity: As Per your requirement\u00a0</strong></li>\n<li><strong>Lifting Height: As Per your requirement</strong></li>\n<li><strong>Span:</strong> <strong>As Per your requirement</strong></li>\n<li>Duly Painted and Ready to use.</li>\n<li><strong>Note: </strong>Portable Gantry Crane is Customized Product, for Quotation\u00a0<strong><em>Kindly email us Required Capacity, Lifting Height, Span </em></strong><em>\u00a0so we will submit our Offer\u00a0</em></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-5-1.jpeg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-5-1.jpeg 1536w, https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-5-1-225x300.jpeg 225w, https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-5-1-768x1024.jpeg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-5-1-1152x1536.jpeg 1152w, https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-5-1-68x90.jpeg 68w, https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-5-1-263x350.jpeg 263w, https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-5-1-360x480.jpeg 360w, https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-5-1-1170x1560.jpeg 1170w, https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-5-1-270x360.jpeg 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane-3-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane-3-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane-3-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-3-150x150.jpeg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-3-150x150.jpeg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-3-170x170.jpeg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-1-150x150.jpeg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-1-150x150.jpeg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Portable-Gantry-Crane.-KEPGC-1-170x170.jpeg 170w"
                    ]
                ]
            }
        ],
        "Dock Levellers & Dock Ramp": [
            {
                "link": "https://www.kijeka.com/product/dock-levellers/",
                "name": "Dock Levellers",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Dock levellers are designed &amp; Manufactured with the aim to create a movable bridge between the loading /unloading area &amp; the surface of a vehicle levelling out differences in height</li>\n<li>Electric Hydraulic Dock leveller is ideal for high usage dock areas</li>\n<li>Operator pushes &amp; Holds the \u201cRaise\u201d button which activates the hydraulic pump &amp; raises the deck when the deck reaches the raised position the lip automatically extends</li>\n<li>The Operator releases the \u201cRaise\u201d button &amp; Deck descends to rest on the trailer</li>\n<li>Control Box Includes red emergency stop button standard. When the truck pulls away, the deck descends to full down position, trips the limit switch and returns automatically to the level support cross traffic position</li>\n<li><strong>Note: Colour &amp; Special Specification can be made according to the customer\u2019s Demands.</strong></li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td style=\"text-align: center;\" width=\"234\"><strong>Model</strong></td>\n<td width=\"288\"><strong>Dock Levellers</strong></td>\n</tr>\n<tr>\n<td width=\"234\">MOC</td>\n<td width=\"288\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"234\">Lifting capacity Option</td>\n<td width=\"288\">8000 Kgs, 10,000 Kgs, 12,000 Kgs</td>\n</tr>\n<tr>\n<td width=\"234\">Top Platform Sizes</td>\n<td width=\"288\">2440 X 1830 MM</td>\n</tr>\n<tr>\n<td width=\"234\">Lip Board Size (mm)</td>\n<td width=\"288\">\u00a0+400-300</td>\n</tr>\n<tr>\n<td width=\"234\">Motor Power( Kw)</td>\n<td width=\"288\">\u00a0 0.75 Kw</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/aaa.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/aaa.png 548w, https://www.kijeka.com/wp-content/uploads/2017/11/aaa-300x141.png 300w, https://www.kijeka.com/wp-content/uploads/2017/11/aaa-270x127.png 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img2-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img2-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/11/img2-170x170.png 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img3-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img3-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/11/img3-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/dock-ramp-portable-steel-yard-ramp/",
                "name": "Dock Ramp (Portable Steel Yard Ramp)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Mobile dock ramp can be applied on sundry occasions such as the position in the non-loading platform, not fixed load and unload location, narrow load and unload ground and so on.</li>\n<li>Mobile forklift truck and other transporting facilities can enter into the truck to carry on loading and unloading directly.</li>\n<li>Provided with manual hydraulic controls.</li>\n<li>Tires can be folded to lift off when the dock is in use and let down when you need to move the mobile dock.</li>\n<li>Easy and convenient to move and change the working location of the mobile dock by the manpower</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<thead>\n<tr>\n<td style=\"text-align: center;\" width=\"102\"><strong>Model</strong></td>\n<td width=\"390\"><strong>Dock Ramp(Portable Steel Yard Ramp)</strong></td>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>Capacity</td>\n<td width=\"390\">10,000 kgs</td>\n</tr>\n<tr>\n<td>Platform Size</td>\n<td width=\"390\"></td>\n</tr>\n<tr>\n<td>A</td>\n<td width=\"390\">6000 mm</td>\n</tr>\n<tr>\n<td>B</td>\n<td width=\"390\">3000 mm</td>\n</tr>\n<tr>\n<td>C</td>\n<td width=\"390\">1000 mm</td>\n</tr>\n<tr>\n<td>D</td>\n<td width=\"390\">300 mm</td>\n</tr>\n<tr>\n<td>E</td>\n<td width=\"390\">10300 mm</td>\n</tr>\n<tr>\n<td>F</td>\n<td width=\"390\">1800 mm</td>\n</tr>\n<tr>\n<td>G</td>\n<td width=\"390\">2100 mm</td>\n</tr>\n<tr>\n<td>H</td>\n<td width=\"390\">1100 mm</td>\n</tr>\n<tr>\n<td>J</td>\n<td width=\"390\">1600 mm</td>\n</tr>\n<tr>\n<td>I</td>\n<td width=\"390\">500 mm</td>\n</tr>\n</tbody>\n</table>\n<p><strong>**The specifications mentioned above are standard and can be customized 100%, according to the customer need.</strong></p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img4.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img4.png 472w, https://www.kijeka.com/wp-content/uploads/2017/11/img4-300x232.png 300w, https://www.kijeka.com/wp-content/uploads/2017/11/img4-270x209.png 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img5-150x150.png"
                    ]
                ]
            }
        ],
        "Drum Equipments": [
            {
                "link": "https://www.kijeka.com/product/below-hook-hoist-mounted-drum-lifter/",
                "name": "Below Hook/Hoist Mounted Drum Lifter",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Vertical Drum Lifter use for easy lifting and transporting of Drum with Help of EOT Crane, Chain pulley block or forklift attachment</li>\n</ul>\n<ul>\n<li>Allows quick, gentle loading and keeps drums upright during lift, reducing spills and injuries.</li>\n<li>All-steel construction.</li>\n</ul>\n<ul>\n<li>Loading Capacity: 500 Kgs</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li style=\"list-style-type: none;\">\n<ul>\n<li>Moving of Drums/Barrels in Vertical Position.</li>\n<li>Use for loading unloading Drums from vehicle , Vertical Stacking Drum one over the other</li>\n</ul>\n</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Options:</strong></p>\n<ul>\n<li style=\"list-style-type: none;\">\n<ul>\n<li>Designs: Different Designs for Different Application Or usage</li>\n</ul>\n</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-768x768.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-270x270.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-370x370.jpg 370w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-2-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-2-768x768.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-2-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-2-270x270.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-2-370x370.jpg 370w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-2-170x170.jpg 170w, https://www.kijeka.com/wp-content/uploads/2017/06/Hoist-Mounted-Drum-Lifter-2.jpg 1000w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/chain-drum-lifter/",
                "name": "Chain Drum Lifter",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>All Steel Construction;\u00a0Easy Moves and Handles open or closed head, Loaded MS Drums</li>\n<li><strong>Capacity: 350 kgs.</strong></li>\n<li><strong>For Lifting of Std. 210 liters MS Drums only</strong></li>\n<li><strong>Easy to Use with Overhead hoist or with Fork Lift.</strong></li>\n<li>Allows quick and gentle loading into over packs and keep drums</li>\n<li>Upright during lift, reducing spills and injuries.</li>\n</ul>\n<ul>\n<li style=\"list-style-type: none;\"></li>\n</ul>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Chain-Drum-Lifter-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Chain-Drum-Lifter-scaled.jpg 1231w, https://www.kijeka.com/wp-content/uploads/2021/04/Chain-Drum-Lifter-144x300.jpg 144w, https://www.kijeka.com/wp-content/uploads/2021/04/Chain-Drum-Lifter-493x1024.jpg 493w, https://www.kijeka.com/wp-content/uploads/2021/04/Chain-Drum-Lifter-768x1597.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/Chain-Drum-Lifter-739x1536.jpg 739w, https://www.kijeka.com/wp-content/uploads/2021/04/Chain-Drum-Lifter-985x2048.jpg 985w, https://www.kijeka.com/wp-content/uploads/2021/04/Chain-Drum-Lifter-43x90.jpg 43w, https://www.kijeka.com/wp-content/uploads/2021/04/Chain-Drum-Lifter-168x350.jpg 168w, https://www.kijeka.com/wp-content/uploads/2021/04/Chain-Drum-Lifter-231x480.jpg 231w, https://www.kijeka.com/wp-content/uploads/2021/04/Chain-Drum-Lifter-1170x2432.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2021/04/Chain-Drum-Lifter-270x561.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/counterbalance-fully-powered-drum-lifter-tilter/",
                "name": "Counterbalance Fully Powered Drum Lifter Tilter",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Drum Lifter Tilter provide a safe, ergonomic solution for your most challenging Drum lift, lower, tilt, rotate and dispense.</li>\n<li>Counterbalance Drum Lifter/Tilter are specifically designed to provide precise Drum handling and maneuverability.</li>\n<li>Counterbalance design allows close access to loading and unloading areas</li>\n<li>Their heavy-duty construction will provide years of dependable service</li>\n<li>Operating Type: Battery Operated Walking , Lifting, Tilting, Up-Down</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Transporting, Tilting, Rotating, Dispensing, Pouring at Required Height</li>\n</ul>\n<p>\u00a0</p>\n<table style=\"height: 702px;\" width=\"935\">\n<tbody>\n<tr>\n<td colspan=\"2\" style=\"text-align: center;\"><strong>Model</strong></td>\n<td><strong>Counterbalance Powered Drum Lifter Tilter</strong></td>\n</tr>\n<tr>\n<td>Drive Type</td>\n<td>/</td>\n<td>Electric (Battery Driven)</td>\n</tr>\n<tr>\n<td>Operating Type</td>\n<td>/</td>\n<td>Standing steer type</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>420</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>2400 from Drum Bottom</td>\n</tr>\n<tr>\n<td>Total height</td>\n<td>mm</td>\n<td>1860</td>\n</tr>\n<tr>\n<td>Total length</td>\n<td>mm</td>\n<td>2270</td>\n</tr>\n<tr>\n<td>Total width</td>\n<td>mm</td>\n<td>1170</td>\n</tr>\n<tr>\n<td>Turning radius</td>\n<td>mm</td>\n<td>2150</td>\n</tr>\n<tr>\n<td>Max. Grade ability\n<p>(Fully-loaded/no-load)</p></td>\n<td>%</td>\n<td>3/5</td>\n</tr>\n<tr>\n<td>Driving wheel size</td>\n<td>mm</td>\n<td>\u00d8250*80</td>\n</tr>\n<tr>\n<td>Tire</td>\n<td>/</td>\n<td>Polyurethane</td>\n</tr>\n<tr>\n<td>Brake type</td>\n<td>/</td>\n<td>Electromagnetic braking</td>\n</tr>\n<tr>\n<td>Drive motor power</td>\n<td>kw</td>\n<td>1.2</td>\n</tr>\n<tr>\n<td>Lifting motor power</td>\n<td>kw</td>\n<td>2.2</td>\n</tr>\n<tr>\n<td>Noise level</td>\n<td>db(A)</td>\n<td>\uff1c70</td>\n</tr>\n<tr>\n<td>Battery\u00a0voltage/capacity</td>\n<td>V/Ah</td>\n<td>24/210</td>\n</tr>\n<tr>\n<td>Charger</td>\n<td>V/A</td>\n<td>24/30</td>\n</tr>\n<tr>\n<td>Net weight</td>\n<td>kg</td>\n<td>1050</td>\n</tr>\n<tr>\n<td>Drum rotating range</td>\n<td>\u00b0</td>\n<td>135\u00b0</td>\n</tr>\n</tbody>\n</table>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter-257x300.jpg 257w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter-768x898.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter-876x1024.jpg 876w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter-70x82.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter-270x316.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter-370x433.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter1-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter2-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter3-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter3-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-lifter-tilter3-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drainer-4-wheel-drum-truck/",
                "name": "Drainer 4 Wheel Drum Truck",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>The innovative design of this 4 wheel drum truck to move and dispense a heavy drum with extra safety, ease of use, and versatility</li>\n<li><strong>Drainer 4 Wheel Drum Trucks</strong> Facilitate the moving and dispensing of liquids from a 55 gallon drum into a 5 gallon container (with help of Drum Faucet)</li>\n<li>The double rim saddle elevates the drum to a 14\u2033 drain height for easy horizontal pouring.</li>\n<li>04 Nos Rollers on bed frame rotate the Steel drum without removing it from the truck.</li>\n<li>Duly power coated &amp; ready for use.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Transporting &amp;dispensing of liquids from the Drums with help of Drum Faucet.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Options:</strong></p>\n<ul>\n<li>Wheels: Polyurethane/Rubber</li>\n<li>MOC- Stainless Steel Mirror-Matt Finish.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"485\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"210\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"275\"><strong>Drainer 4 Wheel Drum Truck</strong></td>\n</tr>\n<tr>\n<td>Capacity</td>\n<td width=\"49\">kgs</td>\n<td width=\"275\">400</td>\n</tr>\n<tr>\n<td>Wheel Dimension</td>\n<td width=\"49\">mm</td>\n<td width=\"275\">\u00d8200*50, \u00d8150*50, \u00d875*25</td>\n</tr>\n<tr>\n<td>Operating Type</td>\n<td width=\"49\"></td>\n<td width=\"275\">Manual Push-Pull, Mechanical Locking</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drain-4-Wheeler-Drum-Truck.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drain-4-Wheeler-Drum-Truck.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Drain-4-Wheeler-Drum-Truck-300x215.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Drain-4-Wheeler-Drum-Truck-768x551.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Drain-4-Wheeler-Drum-Truck-70x50.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Drain-4-Wheeler-Drum-Truck-270x194.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Drain-4-Wheeler-Drum-Truck-370x265.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drum-dollies-2/",
                "name": "Drum Dollies",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Put your drum or barrel on wheels-provides safe and economical drum Transport.</li>\n<li>Drum Dollies having all swivel casters ensure extreme mobility.</li>\n</ul>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Moving of Drums/Barrels in Vertical Position with Lower Ground clearance.</li>\n</ul>\n<p><strong>Options:</strong></p>\n<ul>\n<li>MOC- Stainless Steel Mirror-Matt Finish</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"536\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"312\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"224\"><strong>Drum Dollies</strong></td>\n</tr>\n<tr>\n<td>Capacity</td>\n<td width=\"102\">kgs</td>\n<td width=\"224\">350</td>\n</tr>\n<tr>\n<td>Operating Type</td>\n<td width=\"102\"></td>\n<td width=\"224\">Manual Push-Pull</td>\n</tr>\n<tr>\n<td>Designs</td>\n<td width=\"102\"></td>\n<td width=\"224\">Different Designs for Different usage</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/611VmAwr8TL1.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/611VmAwr8TL1.png 250w, https://www.kijeka.com/wp-content/uploads/2017/12/611VmAwr8TL1-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/12/611VmAwr8TL1-170x170.png 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Dollies.-KE105C-12-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Dollies.-KE105C-12-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Dollies.-KE105C-12-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Dolley-Angle-Type-150x134.jpg"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Dolley-Try-type-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Dolley-Try-type-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Dolley-Try-type-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drum-lever-bar/",
                "name": "Drum Lever Bar/Drum Positioning Tool",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Drum lever bars are designed to move steel drums by rotating them.</strong></li>\n<li><strong>Suitable for tight-head steel drums, this lever bar connects to the upper lip of the drum. Rotate the drum manually, using the of leverage to ease the effort.</strong></li>\n<li>Once connected to the top lip of the drum the bar can be pulled to rotate/move the drum in the required direction. The bar should be repositioned to make the next movement, to move the drum in the opposite direction simply turn the lever bar over.</li>\n<li>Safe working load (SWL):\u00a0 350kg</li>\n<li>Mild Steel construction with Paint Or Powder Coated finish</li>\n</ul>\n<p><u><strong>Drum lever bars\u00a0used for:</strong></u></p>\n<ul>\n<li>Moving a drum to the edge of a pallet to allow it to be picked up by a drum depalletize.</li>\n<li>Move drums closer together on a pallet so that no drums are overhanging the pallet. This may be necessary if the drum has been placed on a pallet using a forklift.</li>\n<li>Drums can be orientated so that the discharge bung or labels are in the correct orientation.</li>\n</ul>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Lever-Bar.-KEDPT.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Lever-Bar.-KEDPT.jpg 496w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Lever-Bar.-KEDPT-300x291.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Lever-Bar.-KEDPT-70x68.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Lever-Bar.-KEDPT-270x262.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Lever-Bar.-KEDPT-370x359.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drum-palletizer-that-pour/",
                "name": "Drum Palletizer that Pour Drum",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-2-copy-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-2-copy-scaled.jpg 2079w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-2-copy-244x300.jpg 244w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-2-copy-831x1024.jpg 831w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-2-copy-768x946.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-2-copy-1247x1536.jpg 1247w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-2-copy-1663x2048.jpg 1663w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-2-copy-70x86.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-2-copy-270x333.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-2-copy-370x456.jpg 370w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-2-copy-1170x1441.jpg 1170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-1-copy-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-1-copy-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Palletizer-with-Pour-Drum.-KEDTF450DT-1-copy-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drum-storage-rack-fix/",
                "name": "Drum Storage Rack (Fix)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>3 Drum Storage Rack/ Stand Fix type for Dispensing Liquid\u00a0</strong></li>\n<li>Storage Racks use for store 210 litre Drum in tight Space</li>\n<li><strong>Allows easy access to drain cocks</strong></li>\n<li>MS Structure with\u00a0 Powder coated finish.</li>\n</ul>\n<p><strong>Application:</strong></p>\n<ul>\n<li><strong>Horizontal Drum Storage &amp; Dispensing Liquids</strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104T-New-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104T-New-scaled.jpg 2560w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104T-New-300x154.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104T-New-1024x525.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104T-New-768x393.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104T-New-1536x787.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104T-New-2048x1049.jpg 2048w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104T-New-70x36.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104T-New-270x138.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104T-New-370x190.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104T-New-1170x599.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drum-tilter-trolleys/",
                "name": "Drum Tilter Trolleys",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>A range of premium drum tilter / transporter trolleys made from\u00a0powder-coated steel for 210 litre steel and plastic drums and barrels.\u00a0</strong></li>\n<li><strong>Lifts, holds, carries, transports, mixes, turns and tilts</strong></li>\n<li><strong>Capacity kg:</strong> 380 kgs</li>\n<li>One-person operation</li>\n<li>Ratchet drum clamp mechanism</li>\n<li>3 position for\u00a0 Tilting /dispensing with auto-locking Pin</li>\n<li>Rotates through 360 deg.</li>\n<li>Highly maneuverable</li>\n<li>Two fixed wheels and one rear castor</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Manual-Drum-Tilter.-KE103N-_Website-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Manual-Drum-Tilter.-KE103N-_Website-scaled.jpg 2560w, https://www.kijeka.com/wp-content/uploads/2020/05/Manual-Drum-Tilter.-KE103N-_Website-300x291.jpg 300w, https://www.kijeka.com/wp-content/uploads/2020/05/Manual-Drum-Tilter.-KE103N-_Website-1024x993.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2020/05/Manual-Drum-Tilter.-KE103N-_Website-768x744.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Manual-Drum-Tilter.-KE103N-_Website-1536x1489.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2020/05/Manual-Drum-Tilter.-KE103N-_Website-2048x1985.jpg 2048w, https://www.kijeka.com/wp-content/uploads/2020/05/Manual-Drum-Tilter.-KE103N-_Website-70x68.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Manual-Drum-Tilter.-KE103N-_Website-270x262.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Manual-Drum-Tilter.-KE103N-_Website-370x359.jpg 370w, https://www.kijeka.com/wp-content/uploads/2020/05/Manual-Drum-Tilter.-KE103N-_Website-1170x1134.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drum-trolley-multipurpose/",
                "name": "Drum Trolley (Multipurpose)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Moving of Drums/Barrels in Vertical Position with Lower Ground clearance.</li>\n<li><strong>Trolley Also use as Oil/Fuel Dispensing system which having Pneumatic pump Holder, Hose Reel Holding.</strong></li>\n</ul>\n<p>\u00a0</p>\n<table width=\"485\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"210\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"275\"><strong>Drum Trolley (Multipurpose) </strong></td>\n</tr>\n<tr>\n<td>Capacity</td>\n<td width=\"49\">kgs</td>\n<td width=\"275\">400</td>\n</tr>\n<tr>\n<td>Net Weight</td>\n<td width=\"49\">Kgs</td>\n<td width=\"275\">50</td>\n</tr>\n<tr>\n<td>Wheel Dimension</td>\n<td width=\"49\">mm</td>\n<td width=\"275\">\u00d8150*50</td>\n</tr>\n<tr>\n<td>Operating Type</td>\n<td width=\"49\"></td>\n<td width=\"275\">Manual Push-Pull, Mechanical Locking</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Trolley.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drum-truck-3-wheel/",
                "name": "Drum Trolley 3 Wheelers",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Three Wheeler- Drum Lifter/Drum Trolley for Better Safety</strong></li>\n<li><strong>For Easy Lifting, Shifting &amp; Transporting of Drums/Barrels\u00a0</strong></li>\n<li>Drum Lifter Suitable for almost 210 Liter Standard MS &amp; HDPE Drums.</li>\n<li>Trolley base on \u00a010\u201dx2\u201d Wheels 02 Nos &amp;\u00a0 6\u201d Caster Wheel-01 no for Best movement</li>\n<li>Manual Push-Pull With Mechanical Locking for best Drum Locking/ Holding</li>\n<li>Zero mechanism, zero mountainous, easy to operate.</li>\n<li>One man cane handles all.</li>\n<li>Duly Powder Coated Finish &amp; Ready for use.</li>\n</ul>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Moving/Transporting of Drums.</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-3-Wheeler.-KE101-HP.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-3-Wheeler.-KE101-HP.jpg 2549w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-3-Wheeler.-KE101-HP-300x246.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-3-Wheeler.-KE101-HP-1024x839.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-3-Wheeler.-KE101-HP-768x629.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-3-Wheeler.-KE101-HP-1536x1258.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-3-Wheeler.-KE101-HP-2048x1678.jpg 2048w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-3-Wheeler.-KE101-HP-70x57.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-3-Wheeler.-KE101-HP-270x221.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-3-Wheeler.-KE101-HP-370x303.jpg 370w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-3-Wheeler.-KE101-HP-1170x958.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drum_trolley/",
                "name": "Drum Trolley 3 Wheelers (PW3-New)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<p><strong>Application:</strong></p>\n<ul>\n<li>It is\u00a0used\u00a0for moving/transporting\u00a0drums from one place to other</li>\n<li>It is useful for handling STD MS/HDEP\u00a0drums of 210 litres.</li>\n</ul>\n<p><strong>Capacity: </strong>350-400 kgs</p>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101-N-PW3-1-copy-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101-N-PW3-1-copy-scaled.jpg 2560w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101-N-PW3-1-copy-300x176.jpg 300w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101-N-PW3-1-copy-1024x599.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101-N-PW3-1-copy-768x450.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101-N-PW3-1-copy-1536x899.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101-N-PW3-1-copy-2048x1199.jpg 2048w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101-N-PW3-1-copy-70x41.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101-N-PW3-1-copy-270x158.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101-N-PW3-1-copy-370x217.jpg 370w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101-N-PW3-1-copy-1170x685.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drum-trolley-3-wheelers-pw3/",
                "name": "Drum Trolley 3 Wheelers (PW3)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Drum Truck/Drum Trolley- For Easy lifting, Moving and transporting of all Standard 210 litres HDPE &amp; MS Drums</li>\n<li><strong>Front Pneumatic (Air Filled) Wheels-02 Nos &amp; Rear Hard Polymer wheels-01</strong> Nos Fitted with Double ball Bearing for smooth movement on rough Outdoor Surface</li>\n<li>Manual Push-Pull With Mechanical Locking for best Drum Locking/ Holding</li>\n<li>Trolley with power coated finish &amp; ready for use.</li>\n</ul>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Transporting of Drums/Barrels</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Truck-3-Wheeler.-KE101PW3.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Truck-3-Wheeler.-KE101PW3.jpg 2155w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Truck-3-Wheeler.-KE101PW3-300x264.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Truck-3-Wheeler.-KE101PW3-1024x902.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Truck-3-Wheeler.-KE101PW3-768x676.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Truck-3-Wheeler.-KE101PW3-1536x1353.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Truck-3-Wheeler.-KE101PW3-2048x1804.jpg 2048w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Truck-3-Wheeler.-KE101PW3-70x62.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Truck-3-Wheeler.-KE101PW3-270x238.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Truck-3-Wheeler.-KE101PW3-370x326.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Truck-3-Wheeler.-KE101PW3-1170x1030.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drum-truck-4-wheel/",
                "name": "Drum Trolley 4 Wheelers (PW4)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>4 Wheeler Drum Truck/Drum Trolley</strong></li>\n<li>For Easy lifting, Moving and transporting of all Standard 210 litres HDPE &amp; MS Drums</li>\n<li><strong>Front Pneumatic (Air Filled) Wheels-02 Nos &amp; Rear Hard Polymer Caster wheels-02</strong> Nos Fitted with Double ball Bearing for smooth movement on rough Outdoor Surface</li>\n<li>Manual Push-Pull With Mechanical Locking for best Drum Locking/ Holding</li>\n<li>Trolley with power coated finish &amp; ready for use.</li>\n<li><strong>Application:</strong>\n<ul>\n<li>Lifting, Transporting of Drums/Barrels</li>\n</ul>\n</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-4-Wheeler-2.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-4-Wheeler-2.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-4-Wheeler-2-300x234.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-4-Wheeler-2-768x600.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-4-Wheeler-2-70x55.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-4-Wheeler-2-270x211.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Truck-4-Wheeler-2-370x289.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drumtrolley-open-top-drum/",
                "name": "Drum Trolley-3 Wheel (Open Top Drum)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Moving/Transporting of <strong>Open Top Drum</strong></li>\n</ul>\n<p><strong>Operating Type:\u00a0</strong></p>\n<ul>\n<li>Manual Push-Pull, Mechanical Locking Drum Rim Clamp</li>\n</ul>\n<p><strong>Capacity: </strong>400Kgs</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler-copy.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler-copy.jpg 2109w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler-copy-248x300.jpg 248w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler-copy-847x1024.jpg 847w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler-copy-768x928.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler-copy-1271x1536.jpg 1271w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler-copy-1694x2048.jpg 1694w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler-copy-70x85.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler-copy-270x326.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler-copy-370x447.jpg 370w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler-copy-1170x1414.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drum-trolley/",
                "name": "Drum Truck- 3 Wheeler (New)",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101N-6-copy-1.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101N-6-copy-1.jpg 1258w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101N-6-copy-1-190x300.jpg 190w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101N-6-copy-1-649x1024.jpg 649w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101N-6-copy-1-768x1211.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101N-6-copy-1-974x1536.jpg 974w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101N-6-copy-1-57x90.jpg 57w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101N-6-copy-1-222x350.jpg 222w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101N-6-copy-1-304x480.jpg 304w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101N-6-copy-1-1170x1845.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Truck-3-Wheeler.-KE101N-6-copy-1-270x426.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/drum-wrench/",
                "name": "Drum Wrench",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Drum Wrench is useful Tool for opening DrumPlugs Or Cap.</li>\n<li>Non-Sparking Wrench fits perfectly onto 2\u2033 &amp; \u00be\u201d Drum Plugs.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Options:</strong></p>\n<ul>\n<li>Designs: Different Designs.</li>\n<li>MOC : Aluminium, Bronze Alloy.</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Wrench1.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Wrench1.jpg 500w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Wrench1-300x106.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Wrench1-70x25.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Wrench1-270x96.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Wrench1-370x131.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Wrench2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Wrench2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Wrench2-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Wrench3-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Wrench3-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Wrench3-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/fork-lift-crane-mounded-drumrotator/",
                "name": "Fork Lift / Crane Mounded DrumRotator",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Professional Equipment/ Tool for Lifting, Moving\u00a0 &amp; Rotating 55 gallon\u00a0 steel Drum s Or 200L Double rimmed plastic Drums</li>\n<li>Can be used on Forklift as well as Crane</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Vertical Drum Lifting, Moving , Rotating, Pouring</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"417\">\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td><strong>Fork Lift / Crane Mounded Drum Rotator\u00a0</strong></td>\n</tr>\n<tr>\n<td>Loading</td>\n<td>\u00a0Kgs</td>\n<td>400</td>\n</tr>\n</tbody>\n</table>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Crane-Mounted-Drum-Rotator.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Crane-Mounted-Drum-Rotator.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Crane-Mounted-Drum-Rotator-300x247.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Crane-Mounted-Drum-Rotator-768x632.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Crane-Mounted-Drum-Rotator-70x58.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Crane-Mounted-Drum-Rotator-270x222.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Crane-Mounted-Drum-Rotator-370x305.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Crane-Mounted-Drum-Rotator1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Crane-Mounted-Drum-Rotator1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Crane-Mounted-Drum-Rotator1-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Crane-Mounted-Drum-Rotator2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Crane-Mounted-Drum-Rotator2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Crane-Mounted-Drum-Rotator2-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/fork-lift-drum-dumper-drum-dispenser/",
                "name": "Fork Lift Drum Dumper/ Drum Dispenser",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Forklift Drum dumper, you can lift and dispense a 50-gallon steel drum or Plastic Drums.</li>\n<li>These forklift drum attachments are simple to mount onto your forks. No tools are needed, and no power connections or truck modifications required</li>\n<li>Control the Drum through pull Chain &amp; the Drum can rotate 360 degree.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Drum Lifting, Rotating, Pouring</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"417\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"180\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"237\"><strong>Fork Lift Drum Dumper/ Drum Dispenser</strong></td>\n</tr>\n<tr>\n<td>Capacity</td>\n<td width=\"37\">kgs</td>\n<td width=\"237\">365</td>\n</tr>\n<tr>\n<td>Fork Opening</td>\n<td width=\"37\">mm</td>\n<td width=\"237\">620</td>\n</tr>\n<tr>\n<td>Fork Pocket</td>\n<td width=\"37\">mm</td>\n<td width=\"237\">185*65</td>\n</tr>\n<tr>\n<td>Drum Rotation Type</td>\n<td width=\"37\"></td>\n<td width=\"237\">Manual Rotation Through Chain</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums-768x767.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums-270x270.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums-370x370.jpg 370w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums2-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/fork-lift-drum-grabs/",
                "name": "Fork Lift Drum Grabs",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>All mechanical automatic clamping mechanisms handle from\u00a0<strong>2 Drums</strong>\u00a0at one time\u00a0without any hydraulic or electrical connections to forklift truck.</li>\n<li>Unique Eagle-grip structure, with automatic adjusting core frame, speedy and safe.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Vertical Drum Lifting, Shifting, Transporting , Loading- Unloading Drum.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"613\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"131\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"235\"><strong>Fork Lift Drum Grabs (For 2-Drums)</strong></td>\n<td width=\"247\"><strong>Fork Lift Drum Grabs (For 1-Drums)</strong></td>\n</tr>\n<tr>\n<td width=\"90\">Loading</td>\n<td width=\"41\">\u00a0Kgs</td>\n<td width=\"235\">360*2</td>\n<td width=\"247\">360*1</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab1.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab1.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab1-300x275.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab1-768x705.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab1-70x64.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab1-270x248.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab1-370x340.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab2-70x71.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab2-270x274.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab2-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab3-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab3-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Forklift-Drum-Grab3-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/fork-lift-drum-grabs-for-4-drums/",
                "name": "Fork Lift Drum Grabs (For 4-Drums)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>All mechanical automatic clamping mechanisms handle from\u00a0<strong>one to four drums</strong>\u00a0at one time\u00a0without any hydraulic or electrical connections to forklift truck</li>\n<li>Unique Eagle-grip structure, with automatic adjusting core frame, speedy and safe.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Vertical Drum Lifting, Shifting, Transporting , Loading- Unloading Drum.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"613\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"131\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"235\"><strong>Fork Lift Drum Grabs</strong><strong>(For 4- Plastic Drums)</strong></td>\n<td width=\"247\">\u00a0\n<p>\u00a0</p>\n<p><strong>Fork Lift Drum Grabs</strong><strong>(For 4- Steel Drums)</strong>\n</p></td>\n</tr>\n<tr>\n<td width=\"90\">Loading</td>\n<td width=\"41\">\u00a0Kgs</td>\n<td width=\"235\">\u00a0500*4</td>\n<td width=\"247\">500*4</td>\n</tr>\n<tr>\n<td width=\"90\">Net Weight</td>\n<td width=\"41\">\u00a0Kgs</td>\n<td width=\"235\">174</td>\n<td width=\"247\">165</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums1.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums1.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums1-298x300.jpg 298w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums1-768x773.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums1-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums1-270x272.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums1-370x373.jpg 370w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums1-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums2-1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums2-1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Fork-Lift-Drum-Graber-4-Drums2-1-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/fully-powered-drum-lifter-tilter/",
                "name": "Fully Powered Drum Lifter Tilter",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Power drive, lift and tilter 55 gallon steel drums &amp; 200L plastic drums.</li>\n<li>Can be operated by one people, labor saving and high work efficiency.</li>\n<li>Drum Lifter/Tilter are specifically designed to provide precise Drum handling and maneuverability.</li>\n<li>Operating Type: Battery Operated Walking , Lifting, Tilting, Up-Down.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Transporting, Tilting, Rotating, Dispensing, Pouring at Required Height.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td><strong>Powered Drum Lifter Tilter</strong></td>\n</tr>\n<tr>\n<td>Drive Type</td>\n<td>/</td>\n<td>Electric(Battery Driven)</td>\n</tr>\n<tr>\n<td>Operating Type</td>\n<td>/</td>\n<td>Standing steer type</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>600</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>2400 from Drum Bottom</td>\n</tr>\n<tr>\n<td>Total height</td>\n<td>mm</td>\n<td>1870</td>\n</tr>\n<tr>\n<td>Total length</td>\n<td>mm</td>\n<td>2270</td>\n</tr>\n<tr>\n<td>Total width</td>\n<td>mm</td>\n<td>1030</td>\n</tr>\n<tr>\n<td>Turning radius</td>\n<td>mm</td>\n<td>1910</td>\n</tr>\n<tr>\n<td>Max. Grade ability\n<p>(Fully-loaded/no-load)</p></td>\n<td>%</td>\n<td>3/5</td>\n</tr>\n<tr>\n<td>Driving wheel size</td>\n<td>mm</td>\n<td>\u00d8250*80</td>\n</tr>\n<tr>\n<td>Tire</td>\n<td>/</td>\n<td>Polyurethane</td>\n</tr>\n<tr>\n<td>Brake type</td>\n<td>/</td>\n<td>Electromagnetic braking</td>\n</tr>\n<tr>\n<td>Drive motor power</td>\n<td>kw</td>\n<td>1.2</td>\n</tr>\n<tr>\n<td>Lifting motor power</td>\n<td>kw</td>\n<td>2.2</td>\n</tr>\n<tr>\n<td>Noise level</td>\n<td>db(A)</td>\n<td>\uff1c70</td>\n</tr>\n<tr>\n<td>Battery\u00a0voltage/capacity</td>\n<td>V/Ah</td>\n<td>24/210</td>\n</tr>\n<tr>\n<td>Charger</td>\n<td>V/A</td>\n<td>24/30</td>\n</tr>\n<tr>\n<td>Net weight</td>\n<td>kg</td>\n<td>680</td>\n</tr>\n<tr>\n<td>Drum rotating range</td>\n<td>\u00b0</td>\n<td>360\u00b0</td>\n</tr>\n</tbody>\n</table>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Lifter-Tilter1.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Lifter-Tilter1.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Lifter-Tilter1-277x300.jpg 277w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Lifter-Tilter1-768x831.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Lifter-Tilter1-946x1024.jpg 946w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Lifter-Tilter1-70x76.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Lifter-Tilter1-270x292.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Lifter-Tilter1-370x400.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Lifter-Tilter2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Lifter-Tilter2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Lifter-Tilter2-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/hydraulic-drum-palletizer-advance-2/",
                "name": "Hydraulic Drum Palletizer-Advance",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Ergonomic solution for lifting, transporting and placing drums on spill or standard pallets.</li>\n<li>Heavy-duty design of 350 KG loading capacity.</li>\n<li>Trolley base on 6\u2033 polyurethane Fix Type wheels 02 Nos&amp; 5\u201dswivel caster with Brake 01 Nos.</li>\n<li>Special Eagle-grip clamps securely hold any steel, plastic or metal-ringed fiber drum.</li>\n<li>Exclusive clamping mechanism which is safety and reliable.</li>\n<li>Operating Type : Manual Push-Pull Type with Special Eagle Grip-Hydraulic Drum Locking system.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Vertical Drum Lifting, Shifting, Transporting , Loading- Unloading From the Pallets &amp; Weighing Scale.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td><strong>Hydraulic Drum Palletizer-Advance\u00a0</strong></td>\n</tr>\n<tr>\n<td>Operating type</td>\n<td>/</td>\n<td>Manual Propel/ Hydraulically Up-Down</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>350</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>300 from Drum Bottom</td>\n</tr>\n<tr>\n<td>Wheel Dimension</td>\n<td>mm</td>\n<td>\u00d8150*50/\u00d8125*50</td>\n</tr>\n<tr>\n<td>Net weight</td>\n<td>kg</td>\n<td>50</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Advance-Drum-Palletizer.-KE101DPC_Website-2.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Advance-Drum-Palletizer.-KE101DPC_Website-2.jpg 1424w, https://www.kijeka.com/wp-content/uploads/2017/06/Advance-Drum-Palletizer.-KE101DPC_Website-2-300x287.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Advance-Drum-Palletizer.-KE101DPC_Website-2-1024x981.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2017/06/Advance-Drum-Palletizer.-KE101DPC_Website-2-768x736.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Advance-Drum-Palletizer.-KE101DPC_Website-2-70x67.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Advance-Drum-Palletizer.-KE101DPC_Website-2-270x259.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Advance-Drum-Palletizer.-KE101DPC_Website-2-370x354.jpg 370w, https://www.kijeka.com/wp-content/uploads/2017/06/Advance-Drum-Palletizer.-KE101DPC_Website-2-1170x1121.jpg 1170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Hydraulic-Drum-Palletizer-Advance4-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Hydraulic-Drum-Palletizer-Advance4-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Hydraulic-Drum-Palletizer-Advance4-70x69.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Hydraulic-Drum-Palletizer-Advance4-270x266.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Hydraulic-Drum-Palletizer-Advance4-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Advance-Drum-Palletizer.-KE101DPC_Website-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Advance-Drum-Palletizer.-KE101DPC_Website-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Advance-Drum-Palletizer.-KE101DPC_Website-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/hydraulic-drum-truck/",
                "name": "Hydraulic Drum Truck",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Our Hydraulic Drum Truck is Designed to allow one worker to easily Lift &amp; Transport the Drum without any kind of efforts.</li>\n<li>This equipment is operated by engaging barrels with a Mechanical- Hydraulic Rim clamp to grasp the top lip.</li>\n<li>Automatic Rim clamping tightening, insure the drum during lifting &amp; Moving which is safety and reliable.</li>\n<li>Ergonomic solution for lifting, transporting and placing 55 gallon Rimmed steel Drums Or HDPE Drum.</li>\n<li>Operating Type : Manual Push-Pull Type with Mechanical-Hydraulic Drum Locking system.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Vertical Drum Lifting, Shifting, Transporting , Loading- Unloading Drum.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td><strong>Hydraulic Drum Truck.</strong></td>\n</tr>\n<tr>\n<td>Operating type</td>\n<td>/</td>\n<td>Manual Propel/ Hydraulically Up-Down</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>300</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>280 from Drum Bottom</td>\n</tr>\n<tr>\n<td>Net weight</td>\n<td>kg</td>\n<td>40</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Hydraulic-Drum-Truck.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Hydraulic-Drum-Truck.jpg 720w, https://www.kijeka.com/wp-content/uploads/2017/06/Hydraulic-Drum-Truck-254x300.jpg 254w, https://www.kijeka.com/wp-content/uploads/2017/06/Hydraulic-Drum-Truck-70x83.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Hydraulic-Drum-Truck-270x319.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Hydraulic-Drum-Truck-370x437.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/low-profile-drum-caddy/",
                "name": "Low-Profile Drum Caddies",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Easily transports 30 or 55 gallon Steel , HDPE, Fiber Drums.</li>\n<li>Use for Vertical Drum transport.</li>\n<li>Caddy Having Removable handle for tilt drum for positioning&amp; features a built in Drum bung nut wrench and Drum seal remover.</li>\n</ul>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Moving of Drums/Barrels in Vertical Position with Lower Ground clearance.</li>\n</ul>\n<p><strong>Options:</strong></p>\n<ul>\n<li>Also available with Fix handle</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"485\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"210\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"275\"><strong>Low-Profile Drum Caddies</strong></td>\n</tr>\n<tr>\n<td>Capacity</td>\n<td width=\"49\">kgs</td>\n<td width=\"275\">500</td>\n</tr>\n<tr>\n<td>Wheel Dimension</td>\n<td width=\"49\">mm</td>\n<td width=\"275\">\u00d8150*50, \u00d875*32</td>\n</tr>\n<tr>\n<td>Operating Type</td>\n<td width=\"49\"></td>\n<td width=\"275\">Manual Push-Pull</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Low-Profile-Drum-Caddies.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Low-Profile-Drum-Caddies.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Low-Profile-Drum-Caddies-300x257.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Low-Profile-Drum-Caddies-768x657.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Low-Profile-Drum-Caddies-70x60.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Low-Profile-Drum-Caddies-270x231.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Low-Profile-Drum-Caddies-370x316.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Low-Profile-Drum-Caddies-Fix-Handle-2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Low-Profile-Drum-Caddies-Fix-Handle-2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Low-Profile-Drum-Caddies-Fix-Handle-2-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/manual-drum-lifter-tilter-2/",
                "name": "Manual Drum Lifter Tilter",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Hydraulically lift and Mechanically \u00a0Rotating for \u00a055 gallon steel drums &amp; 200L plastic drums</li>\n<li>Mechanical Top Drum lip Holding Clamp &amp; Bottom Spring Loaded Lock ensure perfect Drum Holding</li>\n<li>With Help of Gear Box -Rotating Mechanism, Drum Can rotate\u00a0 180\u00b0</li>\n<li>Tilting Or Pouring Liquid at your required height up to 1500mm</li>\n<li>Operating Type: Manual Propel, Hydraulically Up-Down&amp; Tilting ( Rotating) by Mechanical Rotating Mechanism</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Tilting, Rotating, Dispensing, Pouring at Required Height</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td><strong>Powered Drum Lifter Tilter. </strong></td>\n</tr>\n<tr>\n<td>Operating type</td>\n<td>/</td>\n<td>Manual Propel/ Mechanical Rotating</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>450</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>1500 from Drum Bottom</td>\n</tr>\n<tr>\n<td>Pouring Height</td>\n<td>mm</td>\n<td>1680</td>\n</tr>\n<tr>\n<td>Wheel Dimension</td>\n<td>mm</td>\n<td>\u00d8150*50</td>\n</tr>\n<tr>\n<td>Net weight</td>\n<td>kg</td>\n<td>176</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Lifter-Tilter.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Lifter-Tilter.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Lifter-Tilter-193x300.jpg 193w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Lifter-Tilter-768x1194.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Lifter-Tilter-659x1024.jpg 659w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Lifter-Tilter-58x90.jpg 58w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Lifter-Tilter-225x350.jpg 225w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Lifter-Tilter-309x480.jpg 309w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Lifter-Tilter-270x420.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/manual-drum-upender/",
                "name": "Manual Drum Upender",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Manual Drum Upender provides the leverage needed for tilting horizontal drums to the vertical position. </strong></li>\n<li>Constructed of Heavy steel pipe for long life. Wide toe plate prevents denting on barrel sides.</li>\n<li><strong>Uprights filled drums with reduced effort &amp; Reduces back injuries and pinched fingers</strong></li>\n<li>Narrow top plate grabs a variety of chimes. Powder coat finish</li>\n</ul>\n<p><u><strong>Manual Drum Upender Used for:</strong></u></p>\n<ul>\n<li>Moving horizontal Steel drums to the vertical position</li>\n</ul>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Manual-Drum-Upender.KE-TY-50A.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Manual-Drum-Upender.KE-TY-50A.jpg 1603w, https://www.kijeka.com/wp-content/uploads/2021/04/Manual-Drum-Upender.KE-TY-50A-300x204.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Manual-Drum-Upender.KE-TY-50A-1024x696.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2021/04/Manual-Drum-Upender.KE-TY-50A-768x522.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/Manual-Drum-Upender.KE-TY-50A-1536x1044.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2021/04/Manual-Drum-Upender.KE-TY-50A-70x48.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Manual-Drum-Upender.KE-TY-50A-270x184.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Manual-Drum-Upender.KE-TY-50A-370x252.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/Manual-Drum-Upender.KE-TY-50A-1170x796.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/overhead-drum-lifter/",
                "name": "Overhead Drum Lifter",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Below-Hook Drum Lifter with under drum support and positive grip around drum.</li>\n<li><strong>Safety conscious method to lift a steel, plastic or fiber drum with your crane or hoist</strong></li>\n<li>Kijeka Overhead Drum Lifter has under drum support and positive grip to secure around drum with web strap and ratchet</li>\n<li>Holds drum in upright position\u2026 has NO tilt function</li>\n<li>Loading Capacity: 500 Kgs</li>\n</ul>\n<p><strong>Application:</strong></p>\n<ul>\n<li style=\"list-style-type: none;\">\n<ul>\n<li>Moving of Drums/Barrels in Vertical Position.</li>\n<li>Use for loading unloading Drums from vehicle</li>\n</ul>\n</li>\n</ul>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Overhead-Drum-Lifter.-KEODL.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Overhead-Drum-Lifter.-KEODL.jpg 260w, https://www.kijeka.com/wp-content/uploads/2021/04/Overhead-Drum-Lifter.-KEODL-176x300.jpg 176w, https://www.kijeka.com/wp-content/uploads/2021/04/Overhead-Drum-Lifter.-KEODL-53x90.jpg 53w, https://www.kijeka.com/wp-content/uploads/2021/04/Overhead-Drum-Lifter.-KEODL-205x350.jpg 205w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/portable-drum-storage-racks/",
                "name": "Portable Drum Storage Racks",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>3- Drums Storage Rack/ Stand</strong></li>\n<li>Storage Racks use for store 210 Litre\u00a0Drum in tight Space</li>\n<li>Drum racks can be stacked up to 3 high for safe and efficient 210 Litre\u00a0drum storage.</li>\n<li><strong>Horizontal drum racks allow for two-way fork lift access.</strong></li>\n<li><strong>MS Structure with Powder coated finish.</strong></li>\n</ul>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Horizontal Drum Storage, Horizontal Stacking Drum one over the other.</li>\n</ul>\n<p><strong>Options:</strong></p>\n<ul>\n<li>Designs: Different Designs for Different Application Or usage.</li>\n</ul>\n<p>\u00a0</p>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Storage-Racks.-KE104T_Website.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Storage-Racks.-KE104T_Website.jpg 2331w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Storage-Racks.-KE104T_Website-300x202.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Storage-Racks.-KE104T_Website-1024x689.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Storage-Racks.-KE104T_Website-768x517.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Storage-Racks.-KE104T_Website-1536x1034.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Storage-Racks.-KE104T_Website-2048x1379.jpg 2048w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Storage-Racks.-KE104T_Website-70x47.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Storage-Racks.-KE104T_Website-270x182.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Storage-Racks.-KE104T_Website-370x249.jpg 370w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Storage-Racks.-KE104T_Website-1170x788.jpg 1170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Portable-Drum-Storage-Rack3-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Portable-Drum-Storage-Rack3-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Portable-Drum-Storage-Rack3-300x297.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Portable-Drum-Storage-Rack3-768x760.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Portable-Drum-Storage-Rack3-70x69.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Portable-Drum-Storage-Rack3-270x267.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Portable-Drum-Storage-Rack3-370x366.jpg 370w, https://www.kijeka.com/wp-content/uploads/2017/06/Portable-Drum-Storage-Rack3-170x170.jpg 170w, https://www.kijeka.com/wp-content/uploads/2017/06/Portable-Drum-Storage-Rack3.jpg 1000w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/portable-drum-storage-racks-for-2-drums/",
                "name": "Portable Drum Storage Racks (For 2 Drums)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Application:</strong>\n<ul>\n<li><strong>Horizontal Drum Storage, Horizontal Stacking Drum one over the other \u00a0up to 3 high for safe work as Drum storage </strong></li>\n<li><strong>With Help of Drum Faucet work as Drum dispensing station</strong></li>\n</ul>\n<p><strong>Designs:</strong></p>\n<ul>\n<li>Available for 2- Drums, 3-Drums Storage Rack</li>\n</ul>\n<p><strong>Capacity :</strong></p>\n<ul>\n<li>2- Drums Storage Rack Loading Capacity\u00a0 : 720 Kgs</li>\n<li>3- Drums Storage Rack Loading Capacity : 1080 Kgs</li>\n</ul>\n</li>\n</ul>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104D_Website.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104D_Website.jpg 540w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104D_Website-300x133.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104D_Website-70x31.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104D_Website-270x120.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104D_Website-370x164.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/safety-drum-faucets-tap/",
                "name": "Safety Drum Faucets/ Tap",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Simply place these faucets on your drum for leak-proof dispensing of any kind of Low Viscous Chemicals, Solvents, Oils.</strong></li>\n<li>Drum Faucets use for convenient dispensing of media under gravity flow with the drum laid horizontally.</li>\n<li>Stainless Steel construction with a polytetrafluoroethylene (PTFE) seal ensures excellent chemical resistance.</li>\n</ul>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Bucketing, Dispensing Small Amount of Liquid from the drum laid horizontally.</li>\n</ul>\n<p><strong>Options:</strong></p>\n<ul>\n<li>Different Designs/ MOC for Different Application.</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Faucet_All-Type-2-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Faucet_All-Type-2-scaled.jpg 2187w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Faucet_All-Type-2-256x300.jpg 256w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Faucet_All-Type-2-875x1024.jpg 875w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Faucet_All-Type-2-768x899.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Faucet_All-Type-2-1312x1536.jpg 1312w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Faucet_All-Type-2-1750x2048.jpg 1750w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Faucet_All-Type-2-70x82.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Faucet_All-Type-2-270x316.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Faucet_All-Type-2-370x433.jpg 370w, https://www.kijeka.com/wp-content/uploads/2017/06/Drum-Faucet_All-Type-2-1170x1370.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/semi-powered-drum-lifter-tilter-with-manual-rotating/",
                "name": "Semi Powered Drum Lifter Tilter (With Manual Rotating)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Power lift and Manual Hand Rotating for \u00a055 gallon steel drums &amp; 200L plastic drums.</li>\n<li>Two-stage vertical-Drum Lifting allow to make max lifting height to 1500mm.</li>\n<li>Mechanical Top Drum lip Holding Clamp &amp; Bottom Spring Loaded Lock ensure perfect Drum Holding.</li>\n<li>With Help of Manual Rotating Mechanism, Drum Can rotate\u00a0 180\u00b0.</li>\n<li>Tilting Or Pouring Liquid at your required height up to 1500mm.</li>\n<li>Loading Capacity: 520 Kgs.</li>\n<li>Operating Type: Manual Propel- Manual Tilting ( Rotating) , Battery OperatedUp-Down.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Tilting, Rotating, Dispensing, Pouring at Required Height.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td><strong>Semi Powered Drum Lifter Tilter</strong></td>\n</tr>\n<tr>\n<td>Operating type</td>\n<td>/</td>\n<td>Manual Propel/ Rotating ,Battery Operated Up-Down</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>520</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>1500 \u00a0from Drum Bottom</td>\n</tr>\n<tr>\n<td>Lifting Speed</td>\n<td>mm/s</td>\n<td>120</td>\n</tr>\n<tr>\n<td>Turning radius</td>\n<td>mm</td>\n<td>1620</td>\n</tr>\n<tr>\n<td>Wheel Dimension</td>\n<td>mm</td>\n<td>\u00d880*55\u00a0\u00a0/\u00a0\u00a0\u00d8150*50</td>\n</tr>\n<tr>\n<td>Pump Unit Power</td>\n<td>Kw/h</td>\n<td>1.5</td>\n</tr>\n<tr>\n<td>Battery</td>\n<td>Ah/V</td>\n<td>120/12</td>\n</tr>\n<tr>\n<td>Charger</td>\n<td>V/A</td>\n<td>24/30</td>\n</tr>\n<tr>\n<td>Drum rotating range</td>\n<td>\u00b0</td>\n<td>180\u00b0</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating2.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating2.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating2-188x300.jpg 188w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating2-768x1226.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating2-642x1024.jpg 642w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating2-56x90.jpg 56w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating2-219x350.jpg 219w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating2-301x480.jpg 301w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating2-270x431.jpg 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating1-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating3-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating3-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Manual-Rotating3-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/semi-powered-drum-lifter-tilterwith-power-rotating/",
                "name": "Semi Powered Drum Lifter Tilter(With Power Rotating)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Power lift and Power Rotating for 55 gallon steel drums &amp; 200L plastic drums.</li>\n<li>Two-stage vertical-Drum Lifting allow to make max lifting height to 2300mm.</li>\n<li>Mechanical Top Drum lip Holding Clamp &amp; Bottom Spring Loaded Lock ensure perfect Drum Holding.</li>\n<li>With Help of Power Rotating Mechanism, Drum Can rotate 180\u00b0.</li>\n<li>Tilting Or Pouring Liquid at your required height up to 2300mm.</li>\n<li>Loading Capacity: 450 Kgs.</li>\n<li>Operating Type: Manual Propel, Battery OperatedUp-Down&amp;Tilting ( Rotating).</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Tilting, Rotating, Dispensing, Pouring at Required Height.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td><strong>Powered Drum Lifter Tilter</strong></td>\n</tr>\n<tr>\n<td>Operating type</td>\n<td>/</td>\n<td>Manual Propel/ Battery Operated Up-Down &amp; Rotating</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>450</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>2300 from Drum Bottom</td>\n</tr>\n<tr>\n<td>Lifting Speed</td>\n<td>mm/s</td>\n<td>120</td>\n</tr>\n<tr>\n<td>Outline Dimension</td>\n<td>mm</td>\n<td>1880 Height x 1680 Length x 980 Width</td>\n</tr>\n<tr>\n<td>Turning radius</td>\n<td>mm</td>\n<td>1620</td>\n</tr>\n<tr>\n<td>Wheel Dimension</td>\n<td>mm</td>\n<td>\u00d880*55\u00a0\u00a0/\u00a0\u00a0\u00d8150*50</td>\n</tr>\n<tr>\n<td>Pump Unit Power</td>\n<td>Kw/h</td>\n<td>1.5</td>\n</tr>\n<tr>\n<td>Battery</td>\n<td>Ah/V</td>\n<td>120/12</td>\n</tr>\n<tr>\n<td>Charger</td>\n<td>V/A</td>\n<td>24/30</td>\n</tr>\n<tr>\n<td>Net weight</td>\n<td>kg</td>\n<td>343</td>\n</tr>\n<tr>\n<td>Drum rotating range</td>\n<td>\u00b0</td>\n<td>180\u00b0</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Powr-Rotating.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Powr-Rotating.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Powr-Rotating-204x300.jpg 204w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Powr-Rotating-768x1128.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Powr-Rotating-697x1024.jpg 697w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Powr-Rotating-61x90.jpg 61w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Powr-Rotating-238x350.jpg 238w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Powr-Rotating-327x480.jpg 327w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-Tilter-With-Powr-Rotating-270x397.jpg 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-TilterWith-Power-Rotating-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-TilterWith-Power-Rotating-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Lifter-TilterWith-Power-Rotating-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/stand-for-drum-storage-rack/",
                "name": "Stand for Drum Storage Rack",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Application:</strong>\n<ul>\n<li><strong>Horizontal Drum Storage, Drum Dispensing Rack for Liquid Dispensing\u00a0</strong></li>\n<li><strong>With Help of Drum Faucet work as Drum dispensing station</strong></li>\n</ul>\n<p><strong>Designs:</strong></p>\n<ul>\n<li><strong><strong>Available for 2- Drums, 3-Drum dispensing station</strong></strong><strong>/ Storage unit</strong></li>\n</ul>\n<p><strong>Capacity :</strong></p>\n<ul>\n<li>2- Drums Storage Rack Loading Capacity\u00a0 : 720Kgs</li>\n<li>3- Drums Storage Rack Loading Capacity : 1080 Kgs</li>\n</ul>\n</li>\n</ul>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/DrumstandwithTrolley2.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/DrumstandwithTrolley2.jpg 350w, https://www.kijeka.com/wp-content/uploads/2021/04/DrumstandwithTrolley2-300x255.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/DrumstandwithTrolley2-70x60.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/DrumstandwithTrolley2-270x230.jpg 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104DS_New-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104DS_New-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Drum-Storage-Rack.-KE104DS_New-170x170.jpg 170w"
                    ]
                ]
            }
        ],
        "Drum Stirrer": [
            {
                "link": "https://www.kijeka.com/product/drum-stirrer_old/",
                "name": "Drum Stirrer",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Drum Stirrer is ideal for drum mixing when the contents must be thoroughly mixed before they can be pumped out. The propeller diameter of conventional stirrers are too big to be inserted through a bung opening which forces the user to opt for either manual stirring or cut open the barrel to enable the conventional stirrer to be inserted, which makes it cumbersome and time consuming.</li>\n<li>Drum Stirrers, a light, portable and continuous duty rated allows quick blending without removing the drum lid. The Drum Stirrer Assembly incorporates a threaded stainless steel nipple to allow mounting on the opening of drums. Our unique design with foldable propeller with detachable drive motor allows for simple drum stirring.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"563\">\n<tbody>\n<tr>\n<td width=\"186\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"377\"><strong>Drum Stirrer</strong></td>\n</tr>\n<tr>\n<td width=\"186\">Propeller Diameter</td>\n<td width=\"377\">6\u2033 in open condition</td>\n</tr>\n<tr>\n<td width=\"186\">Shaft Length</td>\n<td width=\"377\">32\u2033 for Std 210 Ltr Drum</td>\n</tr>\n<tr>\n<td width=\"186\"><strong>Suitable Drum Type</strong></td>\n<td width=\"377\"><strong>Open Or Closed Type HDPE Or Mild Steel Drum </strong></td>\n</tr>\n<tr>\n<td width=\"186\"><strong>Drive Type</strong></td>\n<td width=\"377\"><strong>Electric Operated Or Pneumatic Operated</strong></td>\n</tr>\n<tr>\n<td width=\"186\">Motor Speed</td>\n<td width=\"377\">1440 RPM</td>\n</tr>\n<tr>\n<td width=\"186\">Max Viscosity</td>\n<td width=\"377\">800 CPS to 8000 CPS</td>\n</tr>\n<tr>\n<td width=\"186\">Application Industries\n<p>\u00a0</p></td>\n<td width=\"377\">Polyurethane, Automobiles, Flavours &amp; Fragrances, Agarbathi, Chemical, Paint and Food Industries.</td>\n</tr>\n<tr>\n<td width=\"186\"><strong>Available For </strong></td>\n<td width=\"377\"><strong>30 / 50 / 100 Ltr Carboys / Containers, 210 Ltr Drums </strong></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Drum-Stirrer.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Drum-Stirrer.png 538w, https://www.kijeka.com/wp-content/uploads/2017/12/Drum-Stirrer-300x130.png 300w, https://www.kijeka.com/wp-content/uploads/2017/12/Drum-Stirrer-270x117.png 270w"
                    ]
                ]
            }
        ],
        "Fuel Pumps, Meters & Acces.": [
            {
                "link": "https://www.kijeka.com/product/continuous-duty-electric-fuel-pump/",
                "name": "Continuous Duty Electric Fuel Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Diesel Transfer Pump, ideal for use on stationary tanks, fixed fuel transferring systems &amp; dispensers and other similar industrial applications.</li>\n<li><strong>Continuous Duty Cyclewith thermal overload protection.</strong></li>\n</ul>\n<p><u>\u00a0</u></p>\n<table width=\"548\">\n<tbody>\n<tr>\n<td width=\"258\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"291\"><strong>Continuous Duty Electric Fuel Pump. </strong></td>\n</tr>\n<tr>\n<td width=\"258\">Drive Type</td>\n<td width=\"291\">Electric Operated</td>\n</tr>\n<tr>\n<td width=\"258\">Flow Rate</td>\n<td width=\"291\">Up to 56 LPM</td>\n</tr>\n<tr>\n<td width=\"258\">Motor Description</td>\n<td width=\"291\">1/2 HP 220V AC, 50 Hz,\u00a0 2800 RPM</td>\n</tr>\n<tr>\n<td width=\"258\">Power Cable Length</td>\n<td width=\"291\">2 Meter</td>\n</tr>\n<tr>\n<td width=\"258\">Duty Cycle:</td>\n<td width=\"291\">Continuous Duty</td>\n</tr>\n<tr>\n<td width=\"228\">Inlet</td>\n<td width=\"291\">1\u201d BSP</td>\n</tr>\n<tr>\n<td width=\"228\">Outlet</td>\n<td width=\"291\">1\u201d BSP</td>\n</tr>\n<tr>\n<td width=\"228\">Wetted Components</td>\n<td width=\"291\"><strong>Aluminium, Nitrile Rubber, Steel, Nylon\u00a0</strong></td>\n</tr>\n<tr>\n<td width=\"228\">Recommended Use</td>\n<td width=\"291\"><strong>Diesel &amp; Kerosene</strong></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Continuous-Duty-Electric-Fuel-Pump.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/electric-fuel-pump/",
                "name": "Electric Fuel Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Heavy duty industrial grade fuel pumps designed for heavy duty use in agriculture, construction, automotive &amp; industrial applications.</li>\n<li>Rain &amp; weather proof for tough outdoor use.</li>\n<li>Lightweight, yet strong non corroding aluminium die cast construction.</li>\n</ul>\n<p><u>\u00a0</u></p>\n<table width=\"548\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"258\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"291\"><strong>Electric Fuel Pump.</strong></td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Drive Type</td>\n<td width=\"291\">Electric Operated</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Flow Rate</td>\n<td width=\"291\">Up to 49 LPM</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Explosion Proof Motor Description</td>\n<td width=\"291\">Heavy Duty 220V AC, 1/8 HP, 50/60 Hz.</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Duty Cycle:</td>\n<td width=\"291\">30 minutes on / 30 minutes off</td>\n</tr>\n<tr>\n<td width=\"228\">Inlet</td>\n<td width=\"30\"></td>\n<td width=\"291\">1\u201d NPT</td>\n</tr>\n<tr>\n<td width=\"228\">Outlet</td>\n<td width=\"30\"></td>\n<td width=\"291\">\u00be\u201d NPT</td>\n</tr>\n<tr>\n<td width=\"228\">Suction Pipe MOC</td>\n<td width=\"30\"></td>\n<td width=\"291\">Steel</td>\n</tr>\n<tr>\n<td width=\"228\">Accuracy</td>\n<td width=\"30\"></td>\n<td width=\"291\">\u00b1 0.50%</td>\n</tr>\n<tr>\n<td width=\"228\">Tank Adapter</td>\n<td width=\"30\"></td>\n<td width=\"291\">2\u201d Threaded</td>\n</tr>\n<tr>\n<td width=\"228\">Hose</td>\n<td width=\"30\"></td>\n<td width=\"291\">3/4\u2033 x 12\u2032 Anti-Static Hose</td>\n</tr>\n<tr>\n<td width=\"228\">Dispensing Nozzle</td>\n<td width=\"30\"></td>\n<td width=\"291\">Aluminium 3/4\u2033 Manual Nozzle with Swivel</td>\n</tr>\n<tr>\n<td width=\"228\">Repeat Ability</td>\n<td width=\"30\"></td>\n<td width=\"291\">\u00b1 0.20%</td>\n</tr>\n<tr>\n<td width=\"228\">Maximum Working Pressure</td>\n<td width=\"30\">PSI</td>\n<td width=\"291\">1,000 PSI (70 BAR)</td>\n</tr>\n<tr>\n<td width=\"228\">Temperature</td>\n<td width=\"30\"><sup>O</sup>C</td>\n<td width=\"291\">-5<sup>O </sup>C to 50 <sup>O</sup></td>\n</tr>\n<tr>\n<td width=\"228\">Minimum Pre Set Qty.</td>\n<td width=\"30\"></td>\n<td width=\"291\">0.10 units</td>\n</tr>\n<tr>\n<td width=\"228\">Maximum Pre Set Qty.</td>\n<td width=\"30\"></td>\n<td width=\"291\">99.9 units</td>\n</tr>\n<tr>\n<td width=\"228\">MAX. Resettable Batch Totalizer</td>\n<td width=\"30\"></td>\n<td width=\"291\">999.9</td>\n</tr>\n<tr>\n<td width=\"228\">MAX. Non Resettable Batch Totalizer</td>\n<td width=\"30\"></td>\n<td width=\"291\">999999 units</td>\n</tr>\n<tr>\n<td width=\"228\">Viscosity of Media Dispensed</td>\n<td width=\"30\">cst</td>\n<td width=\"291\">10 to 5000 cst</td>\n</tr>\n<tr>\n<td width=\"228\">Resolution/ Least Count</td>\n<td width=\"30\">Ltr.</td>\n<td width=\"291\">0.0005 litre</td>\n</tr>\n<tr>\n<td width=\"228\">Water Resistance</td>\n<td width=\"30\"></td>\n<td width=\"291\">IP55</td>\n</tr>\n<tr>\n<td width=\"228\">Wetted Components</td>\n<td width=\"30\"></td>\n<td width=\"291\">Aluminium, Steel, Cast Iron, Nylon, NBR Zinc, Viton, Polypropylene, PVC</td>\n</tr>\n<tr>\n<td width=\"228\">Recommended Use</td>\n<td width=\"30\"></td>\n<td width=\"291\">Petrol , Diesel, E-15 Fuel, Kerosene, Bio Diesel</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Fuel-Pump.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Fuel-Pump.jpg 850w, https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Fuel-Pump-267x300.jpg 267w, https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Fuel-Pump-768x862.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Fuel-Pump-70x79.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Fuel-Pump-270x303.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Fuel-Pump-370x415.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/fuel-control-nozzle/",
                "name": "Fuel Control Nozzle",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>For use with electric fuel pumps &amp; gravity feed applications.</li>\n<li>All metal construction with the body, discharge spout, trigger &amp; guard made from aluminium.</li>\n<li>Manual control also includes continuous flow switch for unattended dispensing.</li>\n<li>Designed for minimal back pressure &amp; reduction in flow.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"606\">\n<tbody>\n<tr>\n<td colspan=\"4\" width=\"411\">\n<p style=\"text-align: center;\"><strong>Models</strong></p>\n</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"212\"><strong>KE 202FCN-19</strong></td>\n<td colspan=\"2\" width=\"199\"><strong>KE 202FCN-25</strong></td>\n</tr>\n<tr>\n<td width=\"101\">Inlet Thread</td>\n<td width=\"111\">3/4\u201d NPT (F)</td>\n<td width=\"94\">Inlet Thread</td>\n<td width=\"105\">1\u201d NPT (F)</td>\n</tr>\n<tr>\n<td width=\"101\">Spout Outer Diameter</td>\n<td width=\"111\">19 mm</td>\n<td width=\"94\">Spout Outer Diameter</td>\n<td width=\"105\">25 mm</td>\n</tr>\n<tr>\n<td width=\"101\">Maximum Flow</td>\n<td width=\"111\">57 LPM</td>\n<td width=\"94\">Maximum Flow</td>\n<td width=\"105\">57 LPM</td>\n</tr>\n<tr>\n<td colspan=\"4\" width=\"411\"><strong>Wetted Components</strong> :Aluminium, Steel, Nylon, Nitrile Rubber</td>\n</tr>\n<tr>\n<td colspan=\"4\" width=\"411\"><strong>Recommended Use: </strong>Diesel, Kerosene &amp; Petrol</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fuel-Control-Nozzle.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/hi-flow-rotary-barrel-pump/",
                "name": "Hi-Flow Rotary Barrel Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Geared Rotary Barrel Pump with 3 times discharge per rotation; for every turn of the handle the rotor turns 3 times</li>\n<li>Aluminium die cast pump with sintered gear driven die cast rotor &amp; vanes</li>\n<li>Complete with 3 pc threaded suction tube for use on 50-210 litre drums.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"548\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"258\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"291\"><strong>Hi-Flow Rotary Barrel Pump.</strong></td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Drive Type</td>\n<td width=\"291\">Manual/ Rotary\u00a0 Operated</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Flow Rate</td>\n<td width=\"291\">Up to 500ML Per Rotation</td>\n</tr>\n<tr>\n<td width=\"228\">Wetted Components</td>\n<td width=\"30\"></td>\n<td width=\"291\">Steel, Aluminium, Zinc, NBR, PVC Nitrile</td>\n</tr>\n<tr>\n<td width=\"228\">Recommended Use</td>\n<td width=\"30\"></td>\n<td width=\"291\">Gasoline, Diesel, Kerosene etc. Works with most petroleum based media &amp; lubricating oils up to SAE 90</td>\n</tr>\n<tr>\n<td width=\"228\">Do Not use with:</td>\n<td width=\"30\"></td>\n<td width=\"291\">Corrosive media, solvents, acids, alkalis etc.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Hi-Flow-Rotary-Barrel-Pump..png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/mechanical-diesel-meter/",
                "name": "Mechanical Diesel Meter",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>High accuracy flow meter with mechanical register</li>\n<li>Dual Mode: Manual &amp; Pre-Set (dispenses set quantity of media &amp; stops)</li>\n<li>Register cap can be easily removed &amp; rotated to every 90\u00b0 orientation for convenient read out</li>\n<li>Robust aluminium die cast construction</li>\n</ul>\n<p><u>\u00a0</u></p>\n<table width=\"548\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"258\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"291\"><strong>Mechanical Diesel Meter. </strong></td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Flow Rate</td>\n<td width=\"291\">\u00a020 to 120 LPM</td>\n</tr>\n<tr>\n<td width=\"210\">Inlet</td>\n<td width=\"48\"></td>\n<td width=\"291\">1\u2033 BSP (F</td>\n</tr>\n<tr>\n<td width=\"210\">Accuracy</td>\n<td width=\"48\"></td>\n<td width=\"291\">\u00b1 1%</td>\n</tr>\n<tr>\n<td width=\"210\">Repeat Ability</td>\n<td width=\"48\"></td>\n<td width=\"291\">\u00b1 0.30 %</td>\n</tr>\n<tr>\n<td width=\"210\">Maximum Working Pressure</td>\n<td width=\"48\">PSI</td>\n<td width=\"291\">145 PSI (10 BAR)</td>\n</tr>\n<tr>\n<td width=\"210\">Temperature</td>\n<td width=\"48\"><sup>O</sup>C</td>\n<td width=\"291\">-10\u00b0C to 60\u00b0C</td>\n</tr>\n<tr>\n<td width=\"210\">MAX. Resettable Batch Totalizer</td>\n<td width=\"48\"></td>\n<td width=\"291\">999 Litres</td>\n</tr>\n<tr>\n<td width=\"210\">MAX. Non Resettable Batch Totalizer</td>\n<td width=\"48\"></td>\n<td width=\"291\">9,99,999 Litres</td>\n</tr>\n<tr>\n<td width=\"210\">Max. Viscosity of Media</td>\n<td width=\"48\"></td>\n<td width=\"291\">2000 cst</td>\n</tr>\n<tr>\n<td width=\"210\">Resolution/ Least Count</td>\n<td width=\"48\"></td>\n<td width=\"291\">0.10 Litres</td>\n</tr>\n<tr>\n<td width=\"210\">Wetted Components</td>\n<td width=\"48\"></td>\n<td width=\"291\">Aluminium, Buthyl Terephthalate, Nitrile Rubber</td>\n</tr>\n<tr>\n<td width=\"210\">Recommended Use</td>\n<td width=\"48\"></td>\n<td width=\"291\">Diesel, Biodiesel, oils with viscosity upto 2000 cSt</td>\n</tr>\n<tr>\n<td width=\"210\">Do Not Use With</td>\n<td width=\"48\"></td>\n<td width=\"291\">Petrol, Water based media</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Mechnical-Diesel-Meter.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Mechnical-Diesel-Meter.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Mechnical-Diesel-Meter-300x288.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Mechnical-Diesel-Meter-768x737.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Mechnical-Diesel-Meter-70x67.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Mechnical-Diesel-Meter-270x259.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Mechnical-Diesel-Meter-370x355.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/rotary-fuel-pump/",
                "name": "Rotary Fuel Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Industry standard for rotary pumps, these are by far the heaviest duty pumps, ideal for tough outdoor use in extreme weather conditions. Suitable for transferring media into smaller container or for quick refuelling of diesel powered vehicles or equipment</li>\n<li>Deliver media with a head / lift up to 20' (6 metres)</li>\n<li>Pump handle rotates a high quality sintered powder metal 3 vane rotor inside a highly finished pumping chamber</li>\n<li>Solid cast iron construction, fully CNC machined to close tolerances.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"548\">\n<tbody>\n<tr>\n<td colspan=\"2\" style=\"text-align: center;\" width=\"258\"><strong>Model</strong></td>\n<td width=\"291\"><strong>Rotary Fuel Pump.</strong></td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Drive Type</td>\n<td width=\"291\">Manual/ Rotary\u00a0 Operated</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Flow Rate</td>\n<td width=\"291\">Up to 38 LPM</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\"></td>\n<td width=\"291\"></td>\n</tr>\n<tr>\n<td width=\"228\">Wetted Components</td>\n<td width=\"30\"></td>\n<td width=\"291\">Cast Iron, Steel, Graphite, Paper, Polypropylene</td>\n</tr>\n<tr>\n<td width=\"228\">Recommended Use</td>\n<td width=\"30\"></td>\n<td width=\"291\">Petroleum based fluids, Oil,\u00a0 Diesel, Petrol, Kerosene, Bio Diesel</td>\n</tr>\n<tr>\n<td width=\"228\">Do Not use with:</td>\n<td width=\"30\"></td>\n<td width=\"291\">Water Based Media</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Fuel-Pump.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Fuel-Pump.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Fuel-Pump-175x300.jpg 175w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Fuel-Pump-768x1315.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Fuel-Pump-598x1024.jpg 598w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Fuel-Pump-53x90.jpg 53w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Fuel-Pump-204x350.jpg 204w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Fuel-Pump-280x480.jpg 280w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Fuel-Pump-270x462.jpg 270w"
                    ]
                ]
            }
        ],
        "Goods Lift": [],
        "Hydraulic Scissor Lift Platform": [
            {
                "link": "https://www.kijeka.com/product/die-loaderroller-lift-table/",
                "name": "Die Loader/Roller Lift Table",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Die Loader Roller Lift Lifting/ Transporting of heavy dies or heavy materials</li>\n<li>Tables enable an operator to lift, lower, move loads and transfer it from floor to floor, vehicle to vehicle and machine to machine</li>\n<li>Scissors are used to elevate the table by applying force through a hydraulic cylinder.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Die Loader/Roller Lift Table </strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Available Top Platform Type</td>\n<td width=\"324\">\u00a0 MS sheet or MS roller type</td>\n</tr>\n<tr>\n<td width=\"198\">Loading capacity Option</td>\n<td width=\"324\">\u00a0 From 350 kg to 1500 kg</td>\n</tr>\n<tr>\n<td width=\"198\">Top Platform Sizes</td>\n<td width=\"324\">\u00a0 As per requirement</td>\n</tr>\n<tr>\n<td width=\"198\">Structure Design</td>\n<td width=\"324\">Single Scissor /Double Scissor Or Multiple</td>\n</tr>\n<tr>\n<td width=\"198\">Lifting Height</td>\n<td width=\"324\">Upto 1500mm</td>\n</tr>\n<tr>\n<td width=\"198\">Available Drive Option</td>\n<td width=\"324\">Manual-Hydraulic, Electric Operated,\n<p>Battery Operated Up-Down</p></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Die-Loader_Roller-Lift-Table.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Die-Loader_Roller-Lift-Table.png 382w, https://www.kijeka.com/wp-content/uploads/2017/11/Die-Loader_Roller-Lift-Table-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/11/Die-Loader_Roller-Lift-Table-300x298.png 300w, https://www.kijeka.com/wp-content/uploads/2017/11/Die-Loader_Roller-Lift-Table-270x268.png 270w, https://www.kijeka.com/wp-content/uploads/2017/11/Die-Loader_Roller-Lift-Table-170x170.png 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Die-Loader_Roller-Lift-Table2-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Die-Loader_Roller-Lift-Table2-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/11/Die-Loader_Roller-Lift-Table2-170x170.png 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Die-Loader_Roller-Lift-Table3-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Die-Loader_Roller-Lift-Table3-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/11/Die-Loader_Roller-Lift-Table3-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/lifting-table-pit-mounted/",
                "name": "Lifting Table- Pit Mounted",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Pit installed dock lifts units allow ground level access for all ranges of material handling equipment without the need for ramps.</li>\n<li>Hydraulic Lift Tables are extremely rugged and reliable machines.</li>\n<li>Lifting table are in use throughout world for machine feeding, work positioning, assembly, order picking, pallet loading, and a wide range of other applications.</li>\n<li>Lift Tables are available in many basic sizes and capacities to lift and position loads up to 10000kgs to heights up to 6000mm.</li>\n<li>The wide range of power options, controls, table tops, and base configurations that can be specified for each of the many basic sizes gives the user an almost unlimited choice of variations.</li>\n<li>Pit mounted dock lifts are available in sizes and capacities to suit the most demanding applications.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Lifting Table-Pit Mounted \u00a0\u00a0</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS- Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Hydraulic-Electrically \u00a0Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Platform Sizes</td>\n<td width=\"324\">\u00b7\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 2600mm\u00a0 x 1500mm\n<p>\u00b7\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 3500mm\u00a0 x 2200mm</p>\n<p>\u00b7\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 <strong>Customised As per requirement</strong></p></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Lifting Height</strong></td>\n<td width=\"324\"><strong>Customised up to 6000mm</strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Available Capacities </strong></td>\n<td width=\"324\"><strong>1,000Kgs to 10,000Kgs \u00a0</strong></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Lifting-Table-Pit-Mounted.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Lifting-Table-Pit-Mounted.png 387w, https://www.kijeka.com/wp-content/uploads/2017/11/Lifting-Table-Pit-Mounted-252x300.png 252w, https://www.kijeka.com/wp-content/uploads/2017/11/Lifting-Table-Pit-Mounted-270x321.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/manual-scissor-lift-table/",
                "name": "Manual Scissor Lift Table",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Scissors lift table uses a scissors mechanism to raise and/or lower goods.</li>\n<li>They are also used to transport these goods over small distances.</li>\n<li>Many industrial operations use lift tables for various purposes, such as vehicle loading and docking, work positioning, handling loads, and as wheelchair lifts.</li>\n<li>Hydraulic Table Truck\u00a0is made of high-strength steel, the design structure is reasonable, safe and stable and reliable, built-in safety valve, sealed cylinder, manual control hydraulic system movements, easy to operate.</li>\n</ul>\n<ul>\n<li>Foot pedal operated hydraulic lifting</li>\n<li>East to operate brake unit</li>\n</ul>\n<p>\u00a0</p>\n<table style=\"height: 424px;\" width=\"737\">\n<tbody>\n<tr>\n<td width=\"138\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td colspan=\"6\" width=\"498\"><strong>Manual Scissor Lift Table</strong></td>\n</tr>\n<tr>\n<td width=\"138\">MOC</td>\n<td colspan=\"6\" width=\"498\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"138\"><strong>Drive Type</strong></td>\n<td colspan=\"6\" width=\"498\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"138\">Available Capacity</td>\n<td width=\"84\">350Kgs</td>\n<td width=\"78\">500Kgs</td>\n<td width=\"84\">1000Kgs</td>\n<td width=\"84\">800Kgs</td>\n<td width=\"84\">1000Kgs</td>\n<td width=\"84\">1500Kgs</td>\n</tr>\n<tr>\n<td width=\"138\">Max. Lifting Height</td>\n<td width=\"84\">1300/1500</td>\n<td width=\"78\">900mm</td>\n<td width=\"84\">1000mm</td>\n<td width=\"84\">1500mm</td>\n<td width=\"84\">1700mm</td>\n<td width=\"84\">1700mm</td>\n</tr>\n<tr>\n<td width=\"138\">Min. Lower Height</td>\n<td width=\"84\">350mm</td>\n<td width=\"78\">280mm</td>\n<td width=\"84\">415mm</td>\n<td width=\"84\">450mm</td>\n<td width=\"84\">500mm</td>\n<td width=\"84\">500mm</td>\n</tr>\n<tr>\n<td width=\"138\">Top Platform-Size(mm)</td>\n<td width=\"84\">905\u00d7500<br/>\nmm</td>\n<td width=\"78\">815\u00d7500<br/>\nmm</td>\n<td width=\"84\">1016\u00d7510<br/>\nmm</td>\n<td width=\"84\">1200\u00d7610<br/>\nmm</td>\n<td width=\"84\">1200\u00d7610<br/>\nmm</td>\n<td width=\"84\">1200\u00d7610<br/>\nmm</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Scissor-Lift-Table.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Scissor-Lift-Table.png 522w, https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Scissor-Lift-Table-300x278.png 300w, https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Scissor-Lift-Table-270x250.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/mobile-scissor-lift-platform-up-to-12-meter/",
                "name": "Mobile Scissor Lift Platform- Up to 12 Meter",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Mobile Scissor lift platform is mainly used for lifting cargo and delivering goods, high-altitude operations.</li>\n<li>It is mainly used to installing, repairing and cleaning high aerial equipment, power equipment, and overhead pipeline and so on. It is widely used to workshop building site, hotel, airport, station, and\u00a0architectural\u00a0decoration\u00a0industry.</li>\n<li>The Table\u00a0is the professional high-altitude operation equipment and widely used for the\u00a0installations and maintenance\u00a0at places like\u00a0warehouse, granary,\u00a0construction sites workshop, railway stations, hotels, airports, gas station and aerial pipeline.</li>\n<li>It\u00a0is\u00a0also\u00a0an\u00a0ideal\u00a0and\u00a0economic\u00a0conveying\u00a0facility\u00a0with\u00a0stable\u00a0lifting,\u00a0simple\u00a0and\u00a0convenient</li>\n</ul>\n<p>Installation and\u00a0low\u00a0electricity\u00a0consumption.</p>\n<ul>\n<li>The product has a safety protection valve to prevent hydraulic pipeline rupture.</li>\n<li>Lifting\u00a0mechanism\u00a0was\u00a0made\u00a0with\u00a0high\u00a0strength\u00a0manganese\u00a0steel\u00a0major\u00a0form.</li>\n<li>Compact\u00a0body\u00a0can\u00a0easily\u00a0pass\u00a0through\u00a0single\u00a0and\u00a0double\u00a0channel\u00a0doorway,\u00a0using\u00a0non-marking\u00a0solid\u00a0tire.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td>\n<p style=\"text-align: center;\"><strong>Model </strong></p>\n</td>\n<td colspan=\"7\"><strong>Mobile Scissor Lift Platform- Up to 12 Meter </strong></td>\n</tr>\n<tr>\n<td colspan=\"8\"><strong>AC Power</strong></td>\n</tr>\n<tr>\n<td><strong>Rated load (kg)</strong></td>\n<td><strong>500 Kgs</strong></td>\n<td><strong>500 Kgs</strong></td>\n<td colspan=\"3\"><strong>500 Kgs</strong></td>\n<td><strong>500 Kgs</strong></td>\n<td><strong>500 Kgs</strong></td>\n</tr>\n<tr>\n<td><strong>Maximum height (m)</strong></td>\n<td><strong>6 Meter </strong></td>\n<td><strong>7.5 Meter</strong></td>\n<td colspan=\"3\"><strong>9 Meter</strong></td>\n<td><strong>11Meter</strong></td>\n<td><strong>12 Meter</strong></td>\n</tr>\n<tr>\n<td>Work Platform Size (m)</td>\n<td>1.85 * 0.88</td>\n<td>1.8 * 1.00</td>\n<td colspan=\"3\">1.8 * 1.00</td>\n<td>2.1 * 1.15</td>\n<td>2.45 * 1.35</td>\n</tr>\n<tr>\n<td>Rise speed (s)</td>\n<td>55</td>\n<td>60</td>\n<td colspan=\"3\">70</td>\n<td>80</td>\n<td>125</td>\n</tr>\n<tr>\n<td>Motor power (kw)</td>\n<td>1.5</td>\n<td>1.5</td>\n<td colspan=\"3\">1.5</td>\n<td>2.2</td>\n<td>3</td>\n</tr>\n<tr>\n<td>Supply voltage (V)</td>\n<td>AC 220/440</td>\n<td>AC 220/440</td>\n<td colspan=\"3\">AC 220/440</td>\n<td>AC 220/440</td>\n<td>AC 220/440</td>\n</tr>\n<tr>\n<td>Tire</td>\n<td>\u00d8200 Polyurethane wheels</td>\n<td colspan=\"4\">\u00d8400-8 Rubber Pneumatic wheel</td>\n<td colspan=\"2\">\u00d8500-8 Rubber pneumatic wheel</td>\n</tr>\n<tr>\n<td>Drive Type</td>\n<td colspan=\"7\">\u00a0AC Lifting-Lowering / Manual Push Pull Type</td>\n</tr>\n<tr>\n<td colspan=\"8\"><strong>DC Power</strong>\n<p><strong>AC Powered, DC Powered,\u00a0 DC Power walking device</strong></p></td>\n</tr>\n<tr>\n<td>Lift Motor</td>\n<td>0.75KW</td>\n<td colspan=\"2\">0.75KW</td>\n<td>0.75KW</td>\n<td colspan=\"2\">0.75KW</td>\n<td>0.75KW</td>\n</tr>\n<tr>\n<td>Battery</td>\n<td>120AH*2</td>\n<td colspan=\"2\">120AH*2</td>\n<td>120AH*2</td>\n<td colspan=\"2\">150AH*2</td>\n<td>150AH*2</td>\n</tr>\n<tr>\n<td>Charger</td>\n<td>4V/15A</td>\n<td colspan=\"2\">4V/15A</td>\n<td>24V/15A</td>\n<td colspan=\"2\">24V/15A</td>\n<td>24V/15A</td>\n</tr>\n<tr>\n<td>Drive Type</td>\n<td colspan=\"7\">\u00a0DC Lifting-Lowering / Manual Push Pull Type</td>\n</tr>\n<tr>\n<td colspan=\"8\"><strong>Motorized Devised with DC Power Drive- Optional</strong></td>\n</tr>\n<tr>\n<td>Drive Motor</td>\n<td>0.75kw</td>\n<td colspan=\"2\">0.75kw</td>\n<td>0.75kw</td>\n<td colspan=\"2\">0.75kw</td>\n<td>0.75kw</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Mobile-Scissor-Lift-Platform-Up-to-12-Meter.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Mobile-Scissor-Lift-Platform-Up-to-12-Meter.png 397w, https://www.kijeka.com/wp-content/uploads/2017/11/Mobile-Scissor-Lift-Platform-Up-to-12-Meter-129x300.png 129w, https://www.kijeka.com/wp-content/uploads/2017/11/Mobile-Scissor-Lift-Platform-Up-to-12-Meter-270x628.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/mobile-scissor-lift/",
                "name": "Mobile Scissor Lift Platform- Up to 16 Meter",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<table>\n<tbody>\n<tr>\n<td colspan=\"3\">\n<p style=\"text-align: center;\"><strong>Model </strong></p>\n</td>\n<td colspan=\"7\"><strong>Mobile Scissor Lift Platform- Up to 16 Meter </strong></td>\n</tr>\n<tr>\n<td colspan=\"10\"><strong>AC Power</strong></td>\n</tr>\n<tr>\n<td colspan=\"3\"><strong>Rated load (kg)</strong></td>\n<td><strong>500 Kgs</strong></td>\n<td><strong>300 Kgs</strong></td>\n<td colspan=\"3\"><strong>1000 Kgs</strong></td>\n<td><strong>1000 Kgs</strong></td>\n<td><strong>1000 Kgs</strong></td>\n</tr>\n<tr>\n<td colspan=\"3\"><strong>Maximum height (m)</strong></td>\n<td><strong>14 Meter </strong></td>\n<td><strong>16 Meter</strong></td>\n<td colspan=\"3\"><strong>6 Meter</strong></td>\n<td><strong>\u00a09Meter</strong></td>\n<td><strong>12 Meter</strong></td>\n</tr>\n<tr>\n<td colspan=\"3\">Work Platform Size (m)</td>\n<td>2.45 * 1.35</td>\n<td>\u00a02.75 * 1.5</td>\n<td colspan=\"3\">1.8 * 1.00</td>\n<td>1.8 * 1.25</td>\n<td>2.45 * 1.35</td>\n</tr>\n<tr>\n<td colspan=\"3\">Rise speed (s)</td>\n<td>165</td>\n<td>173</td>\n<td colspan=\"3\">60</td>\n<td>100</td>\n<td>135</td>\n</tr>\n<tr>\n<td colspan=\"3\">Motor power (kw)</td>\n<td>3</td>\n<td>3</td>\n<td colspan=\"3\">2.2</td>\n<td>3</td>\n<td>4</td>\n</tr>\n<tr>\n<td colspan=\"3\">Supply voltage (V)</td>\n<td>AC 220/440</td>\n<td>AC 220/440</td>\n<td colspan=\"3\">AC 220/440</td>\n<td>AC 220/440</td>\n<td>AC 220/440</td>\n</tr>\n<tr>\n<td colspan=\"3\">Tire</td>\n<td colspan=\"7\">\u00d8500-8 Rubber Pneumatic\n<p>Tire \u00d8500-8 Rubber pneumatic whee</p></td>\n</tr>\n<tr>\n<td colspan=\"2\">Drive Type</td>\n<td colspan=\"8\">\u00a0AC Lifting-Lowering / Manual Push Pull Type</td>\n</tr>\n<tr>\n<td colspan=\"10\"><strong>DC Power</strong>\n<p><strong>AC Powered, DC Powered,\u00a0 DC Power walking device</strong></p></td>\n</tr>\n<tr>\n<td>Lift Motor</td>\n<td colspan=\"3\">2 * 3kw</td>\n<td colspan=\"2\">2 * 3kw</td>\n<td>3kw</td>\n<td colspan=\"2\">3kw</td>\n<td>2.2 \u00d7 3k</td>\n</tr>\n<tr>\n<td>Battery</td>\n<td colspan=\"3\">150AH * 4</td>\n<td colspan=\"2\">150AH * 4</td>\n<td>150AH * 2</td>\n<td colspan=\"2\">200AH * 2</td>\n<td>150AH * 4</td>\n</tr>\n<tr>\n<td>Charger</td>\n<td colspan=\"3\">24V / 30A</td>\n<td colspan=\"2\">24V / 30A</td>\n<td>24V / 15A</td>\n<td colspan=\"2\">24V / 20A</td>\n<td>24V / 30A</td>\n</tr>\n<tr>\n<td>Drive Type</td>\n<td colspan=\"9\">DC Lifting-Lowering / Manual Push Pull Type</td>\n</tr>\n<tr>\n<td colspan=\"10\"><strong>Motorized Devised with DC Power Drive- Optional</strong></td>\n</tr>\n<tr>\n<td>Drive Motor</td>\n<td colspan=\"3\">1.2kw</td>\n<td colspan=\"2\">1.2kw</td>\n<td>0.75kw</td>\n<td colspan=\"2\">1.2kw</td>\n<td>1.2kw</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Mobile-Scissor-Lift-Platform-Up-to-16-Meter.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Mobile-Scissor-Lift-Platform-Up-to-16-Meter.png 397w, https://www.kijeka.com/wp-content/uploads/2017/11/Mobile-Scissor-Lift-Platform-Up-to-16-Meter-129x300.png 129w, https://www.kijeka.com/wp-content/uploads/2017/11/Mobile-Scissor-Lift-Platform-Up-to-16-Meter-270x628.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/self-propelled-scissor-lift-platform-up-to-14-meter/",
                "name": "Self-Propelled Scissor Lift Platform- Up to 14 Meter",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Battery-driven, low noise, pollution-free, suitable for a variety of operating environment</li>\n<li>Automatic pit protection system, more secure and reliable</li>\n<li>One-way extension of the platform, you can quickly reach the operating point</li>\n<li>Fault code automatically displayed to facilitate overhaul</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td>\n<p style=\"text-align: center;\"><strong>Model </strong></p>\n</td>\n<td colspan=\"6\"><strong>Self-Propelled Scissor Lift Platform- Up to 14 Meter </strong></td>\n</tr>\n<tr>\n<td>Safe working load</td>\n<td>230kg</td>\n<td>380kg</td>\n<td>230kg</td>\n<td>450kg</td>\n<td>320kg</td>\n<td>230kg</td>\n</tr>\n<tr>\n<td>Extend the platform safe working load</td>\n<td>113kg</td>\n<td>113kg</td>\n<td>113kg</td>\n<td>113kg</td>\n<td>113kg</td>\n<td>113kg</td>\n</tr>\n<tr>\n<td>The maximum number of workers</td>\n<td>2</td>\n<td>2</td>\n<td>2</td>\n<td>2</td>\n<td>2</td>\n<td>2</td>\n</tr>\n<tr>\n<td>The maximum working height</td>\n<td>7.80m</td>\n<td>8.00m</td>\n<td>10.00m</td>\n<td>10.00m</td>\n<td>12.00m</td>\n<td>13.80m</td>\n</tr>\n<tr>\n<td>The maximum platform height</td>\n<td>5.80m</td>\n<td>6.00m</td>\n<td>8.00m</td>\n<td>8.00m</td>\n<td>10.00m</td>\n<td>11.80m</td>\n</tr>\n<tr>\n<td>Machine length</td>\n<td>1.83m</td>\n<td>2.43m</td>\n<td>2.43m</td>\n<td>2.43m</td>\n<td>2.43m</td>\n<td>2.43m</td>\n</tr>\n<tr>\n<td>Machine width</td>\n<td>0.81m</td>\n<td>0.81m</td>\n<td>0.81m</td>\n<td>1.15m</td>\n<td>1.15m</td>\n<td>1.15m</td>\n</tr>\n<tr>\n<td>Machine height (fence does not fold)</td>\n<td>2.18m</td>\n<td>2.18m</td>\n<td>2.30m</td>\n<td>2.31m</td>\n<td>2.42m</td>\n<td>2.55m</td>\n</tr>\n<tr>\n<td>E machine height (fence fold)</td>\n<td>1.71m</td>\n<td>1.85m</td>\n<td>1.87m</td>\n<td>1.76m</td>\n<td>1.91m</td>\n<td>2.03m</td>\n</tr>\n<tr>\n<td>Working platform size (length * width F)</td>\n<td>1.635m \u00d7 0.745m</td>\n<td>2.27m \u00d7 0.81m</td>\n<td>2.27m \u00d7 0.81m</td>\n<td>2.27m \u00d7 1.12m</td>\n<td>2.27m \u00d7 1.12m</td>\n<td>2.27m \u00d7 1.12m</td>\n</tr>\n<tr>\n<td>Platform extension dimensions</td>\n<td>0.90m</td>\n<td>0.90m</td>\n<td>0.90m</td>\n<td>0.90m</td>\n<td>0.90m</td>\n<td>0.90m</td>\n</tr>\n<tr>\n<td>Wheelbase</td>\n<td>1.36m</td>\n<td>1.87m</td>\n<td>1.87m</td>\n<td>1.87m</td>\n<td>1.87m</td>\n<td>1.87m</td>\n</tr>\n<tr>\n<td>Minimum turning radius (outer wheel)</td>\n<td>1.64m</td>\n<td>2.10m</td>\n<td>2.10m</td>\n<td>2.20m</td>\n<td>2.20m</td>\n<td>2.20m</td>\n</tr>\n<tr>\n<td>Lift / drive motor</td>\n<td>24v / 3.3kw</td>\n<td>24v / 3.3kw</td>\n<td>24v / 3.3kw</td>\n<td>24v / 3.3kw</td>\n<td>24v / 3.3kw</td>\n<td>24v / 4.5kw</td>\n</tr>\n<tr>\n<td>Machine travel speed (folded state)</td>\n<td>3.0km / h</td>\n<td>3.0km / h</td>\n<td>3.0km / h</td>\n<td>3.0km / h</td>\n<td>3.0km / h</td>\n<td>3.0km / h</td>\n</tr>\n<tr>\n<td>Machine traveling speed (lifting state)</td>\n<td>1km / h</td>\n<td>1km / h</td>\n<td>1km / h</td>\n<td>1km / h</td>\n<td>1km / h</td>\n<td>1km / h</td>\n</tr>\n<tr>\n<td>Rise / Fall speed</td>\n<td>18 / 22sec</td>\n<td>35 / 25sec</td>\n<td>40 / 30sec</td>\n<td>40 / 30sec</td>\n<td>60 / 40sec</td>\n<td>70 / 45sec</td>\n</tr>\n<tr>\n<td>Battery</td>\n<td>4 \u00d7 6V / 225Ah</td>\n<td>4 \u00d7 6V / 225Ah</td>\n<td>4 \u00d7 6V / 225Ah</td>\n<td>4 \u00d7 6V / 225Ah</td>\n<td>4 \u00d7 6V / 240Ah</td>\n<td>4 \u00d7 6V / 240Ah</td>\n</tr>\n<tr>\n<td>charger</td>\n<td>24V / 30A</td>\n<td>24V / 30A</td>\n<td>24V / 30A</td>\n<td>24V / 30A</td>\n<td>24V / 30A</td>\n<td>24V / 30A</td>\n</tr>\n<tr>\n<td>Tire</td>\n<td>\u0424305 \u00d7 100</td>\n<td>\u0424380 \u00d7 129</td>\n<td>\u0424380 \u00d7 129</td>\n<td>\u0424380 \u00d7 129</td>\n<td>\u0424380 \u00d7 129</td>\n<td>\u0424380 \u00d7 129</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Self-Propelled-Scissor-Lift-Platform-Up-to-14-Meter.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Self-Propelled-Scissor-Lift-Platform-Up-to-14-Meter.png 317w, https://www.kijeka.com/wp-content/uploads/2017/11/Self-Propelled-Scissor-Lift-Platform-Up-to-14-Meter-102x300.png 102w, https://www.kijeka.com/wp-content/uploads/2017/11/Self-Propelled-Scissor-Lift-Platform-Up-to-14-Meter-270x794.png 270w"
                    ]
                ]
            }
        ],
        "Insect Killer Machine": [
            {
                "link": "https://www.kijeka.com/product/glue-pad-insect-catcher-machine/",
                "name": "Glue Pad Insect Catcher Machine",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>We offer \u2018Glue pad\u2019 Type Insect Killer Machines that are used for both domestic and commercial purposes. Our range is high performing and consumes less power to effectively lure insects &amp; mosquitoes. Our product is reliable and durable and use minimum maintenance.</li>\n<li><strong>Machine Body: Fiber</strong></li>\n<li>Machine size: 21\u2033 x 4.5\u2033 x 13.5\u2033 (LxWxH)</li>\n<li>Glue pad Board Size : 16.5\u2033 x 11.5\u2033 or as per available</li>\n<li>U.V Tubes: 3 No. X 18\u2033/15W (Phillips)</li>\n<li>Power consumption: 45 W</li>\n<li>Effective Area: Outside Area: 250 Sq. Ft.</li>\n<li>Closed Area: 500 Sq.Ft.</li>\n<li>Super white color fiber body, designer shape for best look.</li>\n<li>Fitted with Phillips choke, starter or equivalent &amp; Brass plate tube holder</li>\n<li>For human safety with on/off Rocker switch &amp; fuse holder is\u00a0compulsory.</li>\n<li>Newly introduced &amp; latest technology, Fiber Body.</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Glue-Pad-Insect-Catcher-Machine.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Glue-Pad-Insect-Catcher-Machine.png 496w, https://www.kijeka.com/wp-content/uploads/2017/12/Glue-Pad-Insect-Catcher-Machine-300x228.png 300w, https://www.kijeka.com/wp-content/uploads/2017/12/Glue-Pad-Insect-Catcher-Machine-270x205.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/insect-killer-machine/",
                "name": "Insect Killer Machine",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Insect Killer Model : 2 feet</li>\n<li>Outer Dimension: 25\u201d Length x 8\u201d Width x 18\u201d Height</li>\n<li><strong>Insect Killer Body: MS Powder Coated Or Stainless Steel</strong></li>\n<li><strong>Outer Safety : MS Plastic coted / SS Safety Grill </strong></li>\n<li>Having 18 watts 2- U.V. Tube lights \u2013 Original &amp; Imported.</li>\n<li>UV Tube Wavelength: 350-450 mm</li>\n<li>Input volts: Single phase, 230 volt, 50/60 Hz.</li>\n<li>Steep Rise Transformer Output : 3000 volts/ 3kv</li>\n<li>Power Consumptions: 0.6 units in 8 Hours.</li>\n<li>Input Plug: 3-Core wire with 3-pin Plug</li>\n<li>Insect Killer with 20 W- Electronic Choke specially for U.V. Tubes</li>\n<li>Safety Features: No- Off rocker\u00a0<em>switch</em> with\u00a0 fuse against Power fluctuation</li>\n<li>Powder coted Catch Tray for died insects and easily removable.</li>\n<li>Effective Area of Coverage- Close Room: 500 sq. ft.</li>\n<li>Effective Area of Coverage- Open Area : 300 sq. ft.</li>\n<li><strong><em>Available in Hanging (double Side Open) / Wall Mountable (Single Side Open) Model</em></strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Insect-Killer-Machine.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Insect-Killer-Machine.png 384w, https://www.kijeka.com/wp-content/uploads/2017/12/Insect-Killer-Machine-300x234.png 300w, https://www.kijeka.com/wp-content/uploads/2017/12/Insect-Killer-Machine-270x211.png 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Insect-Killer-Machine2-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Insect-Killer-Machine2-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/12/Insect-Killer-Machine2-170x170.png 170w"
                    ]
                ]
            }
        ],
        "Hand Trucks": [
            {
                "link": "https://www.kijeka.com/product/2-wheeler-generator-trolley/",
                "name": "2 Wheeler Generator Trolley",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><b>Trolley for Generator movement\u00a0</b></li>\n<li>Trolley Made out from Heavy duty MS Channel</li>\n<li>Trolley Fitted with 02 Nos Big Pneumatic Wheel</li>\n<li>Made in India Product</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Generator-Trolley-copy-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Generator-Trolley-copy-scaled.jpg 2560w, https://www.kijeka.com/wp-content/uploads/2020/05/Generator-Trolley-copy-300x109.jpg 300w, https://www.kijeka.com/wp-content/uploads/2020/05/Generator-Trolley-copy-1024x373.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2020/05/Generator-Trolley-copy-768x280.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Generator-Trolley-copy-1536x559.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2020/05/Generator-Trolley-copy-2048x745.jpg 2048w, https://www.kijeka.com/wp-content/uploads/2020/05/Generator-Trolley-copy-70x25.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Generator-Trolley-copy-270x98.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Generator-Trolley-copy-370x135.jpg 370w, https://www.kijeka.com/wp-content/uploads/2020/05/Generator-Trolley-copy-1170x426.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/3-sided-platform-trucks-slattype-sides/",
                "name": "3 Sided Platform Trucks-(SlatType Sides)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Ideal for transporting or staging of bulkier materials.</li>\n<li>All models have 2 swivel, 2 rigid casters with a push bar handle on swivel caster end.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"306\"><strong>3-Sided Platform Trucks (Slat-Type Sides).</strong></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"216\">Sider</td>\n<td width=\"306\">3-Sided Covered</td>\n</tr>\n<tr>\n<td width=\"216\">Available Capacity</td>\n<td width=\"306\">Up to 1000 kgs.</td>\n</tr>\n<tr>\n<td width=\"216\">Standard Top Platform Size</td>\n<td width=\"306\">48\u201d Length X 24\u201d Width X 36\u201d Sider\n<p>48\u201d Length X 30\u201d Width \u00a0X 36\u201d Sider</p>\n<p>60\u201d Length X 30\u201d Width \u00a0X 36\u201d Sider</p></td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Special Platform Size &amp; Sider Height\u00a0 </strong></td>\n<td width=\"306\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">UHMW-PE, Nylon, Pneumatic, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/3-Sided-Platform-Trucks-SlatType-Sides.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/3-sided-platform-trucks-steel-sides/",
                "name": "3 Sided Platform Trucks-(Steel Sides)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Ideal for transporting or staging of bulkier materials.</li>\n<li>Specially designed to move and store bulky merchandise, supplies, parts or packaged goods. Choice of solid metal sheet</li>\n<li>All models have 2 swivel, 2 rigid casters with a push bar handle on swivel caster end.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"306\"><strong>3-Sided Platform Trucks (Steel Sides). </strong></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"216\">Sider</td>\n<td width=\"306\">3-Sided Covered</td>\n</tr>\n<tr>\n<td width=\"216\">Available Capacity</td>\n<td width=\"306\">Up to 1000 kgs.</td>\n</tr>\n<tr>\n<td width=\"216\">Standard Top Platform Size</td>\n<td width=\"306\">48\u201d Length X 24\u201d Width X 36\u201d Sider\n<p>48\u201d Length X 30\u201d Width \u00a0X 36\u201d Sider</p>\n<p>60\u201d Length X 30\u201d Width \u00a0X 36\u201d Sider</p></td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Special Platform Size &amp; Sider Height\u00a0 </strong></td>\n<td width=\"306\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">UHMW-PE, Nylon, Pneumatic, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/3-Sided-Platform-Trucks-Steel-Sides.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/3-Sided-Platform-Trucks-Steel-Sides.png 277w, https://www.kijeka.com/wp-content/uploads/2017/07/3-Sided-Platform-Trucks-Steel-Sides-276x300.png 276w, https://www.kijeka.com/wp-content/uploads/2017/07/3-Sided-Platform-Trucks-Steel-Sides-270x293.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/3-sided-platform-trucks-tubular-sides/",
                "name": "3 Sided Platform Trucks-(Tubular Sides)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Ideal for transporting or staging of bulkier materials.</li>\n<li>All models have 2 swivel, 2 rigid casters with a push bar handle on swivel caster end.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"306\"><strong>3-Sided Platform Trucks (Tubular Sides).</strong></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"216\">Sider</td>\n<td width=\"306\">3-Sided Covered</td>\n</tr>\n<tr>\n<td width=\"216\">Available Capacity</td>\n<td width=\"306\">Up to 1000 kgs.</td>\n</tr>\n<tr>\n<td width=\"216\">Standard Top Platform Size</td>\n<td width=\"306\">48\u201d Length X 24\u201d Width X 36\u201d Sider\n<p>48\u201d Length X 30\u201d Width \u00a0X 36\u201d Sider</p>\n<p>60\u201d Length X 30\u201d Width \u00a0X 36\u201d Sider</p></td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Special Platform Size &amp; Sider Height\u00a0 </strong></td>\n<td width=\"306\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">UHMW-PE, Nylon, Pneumatic, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/3-Sided-Platform-Trucks-Tubular-Sides.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/3-Sided-Platform-Trucks-Tubular-Sides.png 279w, https://www.kijeka.com/wp-content/uploads/2017/07/3-Sided-Platform-Trucks-Tubular-Sides-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/07/3-Sided-Platform-Trucks-Tubular-Sides-270x270.png 270w, https://www.kijeka.com/wp-content/uploads/2017/07/3-Sided-Platform-Trucks-Tubular-Sides-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/6-bucket-wheel-barrows/",
                "name": "6 Bucket Wheel Barrows",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Excellent for collecting &amp; handling waste</li>\n<li>Plastic bins moulded from special UV stabilized grades of polyethylene.</li>\n<li>Rust-free and maintenance-free.</li>\n<li>Light weight and easy to handle.</li>\n<li>Hygienic and easy to clean.</li>\n<li>Strong and durable 6-plastic bins with M.S. handle.</li>\n<li>Rolls effortlessly on 3- heavy duty wheels.</li>\n<li>S. structure will be powder coated.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"577\">\n<tbody>\n<tr>\n<td width=\"186\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"391\"><strong>Wheel Barrows.</strong></td>\n</tr>\n<tr>\n<td width=\"186\">MOC</td>\n<td width=\"391\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"186\">Drive Type</td>\n<td width=\"391\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"186\">Wheel Option</td>\n<td width=\"391\">UHMW-PE, Nylon, Solid Rubber, MS Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Plastic-Bin-Wheel-Barrow.-KE410.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Plastic-Bin-Wheel-Barrow.-KE410.jpg 1929w, https://www.kijeka.com/wp-content/uploads/2020/05/Plastic-Bin-Wheel-Barrow.-KE410-300x206.jpg 300w, https://www.kijeka.com/wp-content/uploads/2020/05/Plastic-Bin-Wheel-Barrow.-KE410-1024x704.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2020/05/Plastic-Bin-Wheel-Barrow.-KE410-768x528.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Plastic-Bin-Wheel-Barrow.-KE410-1536x1057.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2020/05/Plastic-Bin-Wheel-Barrow.-KE410-70x48.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Plastic-Bin-Wheel-Barrow.-KE410-270x186.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Plastic-Bin-Wheel-Barrow.-KE410-370x255.jpg 370w, https://www.kijeka.com/wp-content/uploads/2020/05/Plastic-Bin-Wheel-Barrow.-KE410-1170x805.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/bales-trolley/",
                "name": "Bales Trolley",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Application:</strong>\n<ul>\n<li>Handles bales of cotton, rags, waste paper</li>\n</ul>\n<p><strong>Designs:</strong></p>\n<ul>\n<li><strong>We are leading Manufacturer of huge range of Bale Handling/ Trolley.</strong></li>\n<li>Customize product Available as per Customer design or Sample</li>\n</ul>\n</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart-scaled.jpg 1291w, https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart-151x300.jpg 151w, https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart-516x1024.jpg 516w, https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart-768x1523.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart-774x1536.jpg 774w, https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart-1033x2048.jpg 1033w, https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart-45x90.jpg 45w, https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart-176x350.jpg 176w, https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart-242x480.jpg 242w, https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart-1170x2321.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart-270x536.jpg 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart_3-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart_3-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Bales-Hand-Cart_3-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/bar-cradle-trucks/",
                "name": "Bar Cradle Trucks",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Move and store pipe, channel, bar stock, barrels, or drums with these Heavy-Duty Cradle Carts</li>\n<li>A large open design that makes loading and unloading by fork trucks and slings easy</li>\n<li>Combine multiple Cradle Trucks to support longer loads and for greater capacity.</li>\n<li>Loads on single Cradle Trucks must be centred on truck</li>\n<li><strong><em>Available in different sizes &amp; Wheel Option </em></strong></li>\n</ul>\n<p>\u00a0</p>\n<table width=\"601\">\n<tbody>\n<tr>\n<td width=\"233\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"368\"><strong>Bar Cradle Trucks</strong></td>\n</tr>\n<tr>\n<td width=\"233\">MOC</td>\n<td width=\"368\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"233\">Drive Type</td>\n<td width=\"368\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"233\">Wheel Option</td>\n<td width=\"368\">Nylon, MS, Pneumatic,</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Bar-Cradle-Trucks.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Bar-Cradle-Trucks.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/10/Bar-Cradle-Trucks-300x215.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/10/Bar-Cradle-Trucks-768x550.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/10/Bar-Cradle-Trucks-70x50.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/10/Bar-Cradle-Trucks-270x193.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/10/Bar-Cradle-Trucks-370x265.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Bar-Cradle-Trucks2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Bar-Cradle-Trucks2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/10/Bar-Cradle-Trucks2-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Bar-Cradle-Trucks3-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Bar-Cradle-Trucks3-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/10/Bar-Cradle-Trucks3-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/bin-cart/",
                "name": "Bin Cart",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Ideal for component storage and transfer to assembly or production areas. </strong></li>\n<li><em>Unit comprises of base unit with aluminium chequered top plate fitted with swivel casters-4 nos &amp; a frame on which two louver panels of a size 457mm x 610 can be fitted on a single side.</em></li>\n<li><em>Robust construction, Epoxy powder coated, easy assembly, push pull handle a both sides.</em></li>\n<li>Bottom compartment distance will be 300mm.</li>\n<li><strong><em>Only Trolley Without bins Or with 73 Different Size Bins</em></strong></li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"306\"><strong>Bin Cart.</strong></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"216\">Available Capacity</td>\n<td width=\"306\">Up to 500 kgs.</td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">PU, UHMW-PE, Nylon, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Bin-Cart.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/brick-and-tile-wheel-barrow/",
                "name": "Brick and Tile Wheel Barrow",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Heavy Duty Buggy for carrying a slab of bricks Or Tiles</li>\n<li>Capacity: 250Kg</li>\n<li>Trolley Having single Pneumatic for easy movement</li>\n<li>Best quality In India</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Brick-and-tile-wheelbarrow-copy.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Brick-and-tile-wheelbarrow-copy.jpg 1143w, https://www.kijeka.com/wp-content/uploads/2020/05/Brick-and-tile-wheelbarrow-copy-300x216.jpg 300w, https://www.kijeka.com/wp-content/uploads/2020/05/Brick-and-tile-wheelbarrow-copy-1024x736.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2020/05/Brick-and-tile-wheelbarrow-copy-768x552.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Brick-and-tile-wheelbarrow-copy-70x50.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Brick-and-tile-wheelbarrow-copy-270x194.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Brick-and-tile-wheelbarrow-copy-370x266.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/can-tippers/",
                "name": "Bucket Tippers",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Bucket Tippers make it easy to pour from your 20 Litre round Bucket or can.</strong></li>\n<li>They simplify and speed dispensing, while reducing risks of repetitive lifting.</li>\n<li><strong>Simply set your can or pail into the 20 Litre bucket holder, and adjust the catch assembly to the height of your can. Then it\u2019s readily convenient to dispense from your pail \u2013 just use the top handle to tilt, pivot and pour.</strong></li>\n<li>Eliminate the need to repeatedly lift a heavy 20 Litre pail.</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Can-Tippers-copy.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Can-Tippers-copy.jpg 2480w, https://www.kijeka.com/wp-content/uploads/2020/05/Can-Tippers-copy-300x277.jpg 300w, https://www.kijeka.com/wp-content/uploads/2020/05/Can-Tippers-copy-1024x946.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2020/05/Can-Tippers-copy-768x709.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Can-Tippers-copy-1536x1419.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2020/05/Can-Tippers-copy-2048x1892.jpg 2048w, https://www.kijeka.com/wp-content/uploads/2020/05/Can-Tippers-copy-70x65.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Can-Tippers-copy-270x249.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Can-Tippers-copy-370x342.jpg 370w, https://www.kijeka.com/wp-content/uploads/2020/05/Can-Tippers-copy-1170x1081.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/cart-for-water-bottles/",
                "name": "Cart for Water Bottles",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Water Bottles Cart for 20 liters water bottles, manufactured by \u201cKijeka\u201d<br/>\nCombination of practicality, reliability, ease of use.</strong></li>\n<li>The cart for water is the best choice for reliable and convenient transportation of plastic bottles.</li>\n<li>The maximum placement is possible up to 4 containers, with a volume of 20 liters each.</li>\n<li><strong>The main areas of application are: \u00a0</strong>Logistics companies, Delivery of drinking water, Offices, Industrial enterprises, Shopping centers, Markets, Workshops and utility rooms, farms, private households.</li>\n<li><strong>It can be used for transportation and storage of plastic bottles</strong></li>\n<li><strong>Aesthetic appearance with Powder coated or Paint Finish</strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Water-Bottles-Trolley-copy.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Water-Bottles-Trolley-copy.jpg 546w, https://www.kijeka.com/wp-content/uploads/2020/05/Water-Bottles-Trolley-copy-164x300.jpg 164w, https://www.kijeka.com/wp-content/uploads/2020/05/Water-Bottles-Trolley-copy-49x90.jpg 49w, https://www.kijeka.com/wp-content/uploads/2020/05/Water-Bottles-Trolley-copy-191x350.jpg 191w, https://www.kijeka.com/wp-content/uploads/2020/05/Water-Bottles-Trolley-copy-262x480.jpg 262w, https://www.kijeka.com/wp-content/uploads/2020/05/Water-Bottles-Trolley-copy-270x495.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/chair-trolley/",
                "name": "Chair Trolley",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Plastic Stacking Chair Trolley</li>\n<li>Stack up to 10 High</li>\n<li>Store and move chairs</li>\n<li>Heavy duty steel frame</li>\n<li>Made in India</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Chair-Trolley-copy.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Chair-Trolley-copy.jpg 870w, https://www.kijeka.com/wp-content/uploads/2020/05/Chair-Trolley-copy-300x291.jpg 300w, https://www.kijeka.com/wp-content/uploads/2020/05/Chair-Trolley-copy-768x745.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Chair-Trolley-copy-70x68.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Chair-Trolley-copy-270x262.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Chair-Trolley-copy-370x359.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/cylinder-lift/",
                "name": "Cylinder Lift",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Application:</strong>\n<ul>\n<li><strong>Load, Unload, and Move Cylinders Quickly and Easily Without Destroying Your Back</strong></li>\n<li>\u00a0Ergonomic Cylinder Lift</li>\n<li>Best Option for Loading unloading Cylinder From Vehicle</li>\n</ul>\n<ul>\n<li><strong>Suitable for 9.5\u201d Dia Cylinder</strong></li>\n</ul>\n</li>\n<li><strong>Designs:</strong>\n<ul>\n<li>Ergonomic Cylinder Lift Design</li>\n<li>Quick &amp; Easy Mechanical Lifting &amp; Cylinder Locking Arrangement</li>\n<li>First Time in India, Make in India Product</li>\n</ul>\n</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Cylinders-Lift.-KE412CL-2.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Cylinders-Lift.-KE412CL-2.jpg 1450w, https://www.kijeka.com/wp-content/uploads/2021/04/Cylinders-Lift.-KE412CL-2-189x300.jpg 189w, https://www.kijeka.com/wp-content/uploads/2021/04/Cylinders-Lift.-KE412CL-2-644x1024.jpg 644w, https://www.kijeka.com/wp-content/uploads/2021/04/Cylinders-Lift.-KE412CL-2-768x1220.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/Cylinders-Lift.-KE412CL-2-967x1536.jpg 967w, https://www.kijeka.com/wp-content/uploads/2021/04/Cylinders-Lift.-KE412CL-2-1289x2048.jpg 1289w, https://www.kijeka.com/wp-content/uploads/2021/04/Cylinders-Lift.-KE412CL-2-57x90.jpg 57w, https://www.kijeka.com/wp-content/uploads/2021/04/Cylinders-Lift.-KE412CL-2-220x350.jpg 220w, https://www.kijeka.com/wp-content/uploads/2021/04/Cylinders-Lift.-KE412CL-2-302x480.jpg 302w, https://www.kijeka.com/wp-content/uploads/2021/04/Cylinders-Lift.-KE412CL-2-1170x1859.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2021/04/Cylinders-Lift.-KE412CL-2-270x429.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/cylinder-lifting-cradle/",
                "name": "Cylinder Lifting Cradle",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Oxygen-Cylinder-Lifter.-KE412B-4.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Oxygen-Cylinder-Lifter.-KE412B-4.jpg 500w, https://www.kijeka.com/wp-content/uploads/2020/05/Oxygen-Cylinder-Lifter.-KE412B-4-230x300.jpg 230w, https://www.kijeka.com/wp-content/uploads/2020/05/Oxygen-Cylinder-Lifter.-KE412B-4-70x90.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Oxygen-Cylinder-Lifter.-KE412B-4-268x350.jpg 268w, https://www.kijeka.com/wp-content/uploads/2020/05/Oxygen-Cylinder-Lifter.-KE412B-4-368x480.jpg 368w, https://www.kijeka.com/wp-content/uploads/2020/05/Oxygen-Cylinder-Lifter.-KE412B-4-270x353.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/cylinder-pallet/",
                "name": "Cylinder Pallet",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet.jpg 1693w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-245x300.jpg 245w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-838x1024.jpg 838w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-768x939.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-1256x1536.jpg 1256w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-1675x2048.jpg 1675w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-70x86.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-270x330.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-370x452.jpg 370w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-1170x1431.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/cylinder-pallet-cage/",
                "name": "Cylinder Pallet Cage",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-Cage-copy.png",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-Cage-copy.png 385w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-Cage-copy-220x300.png 220w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-Cage-copy-66x90.png 66w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-Cage-copy-256x350.png 256w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-Cage-copy-351x480.png 351w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Pallet-Cage-copy-270x369.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/gas-cylinder-trucks-for-2-cylinder/",
                "name": "Double Gas Cylinder Cart (2-Wheeler)",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Truck-For-2-Cylinders.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Truck-For-2-Cylinders.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Truck-For-2-Cylinders-186x300.jpg 186w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Truck-For-2-Cylinders-768x1236.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Truck-For-2-Cylinders-636x1024.jpg 636w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Truck-For-2-Cylinders-56x90.jpg 56w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Truck-For-2-Cylinders-217x350.jpg 217w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Truck-For-2-Cylinders-298x480.jpg 298w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Truck-For-2-Cylinders-270x435.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/gas-cylinder-trucks-for-2-cylinder-2/",
                "name": "Double Gas Cylinder Cart (4-Wheeler)",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-2-Cylinder-psd.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-2-Cylinder-psd.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-2-Cylinder-psd-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-2-Cylinder-psd-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-2-Cylinder-psd-768x770.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-2-Cylinder-psd-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-2-Cylinder-psd-270x271.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-2-Cylinder-psd-370x371.jpg 370w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-2-Cylinder-psd-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/gas-cylinder-cart/",
                "name": "Economy Cylinder Carts",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/2-Wheeler-Single-Gas-Cylinder-Trolley.-KE412D-new-copy.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/2-Wheeler-Single-Gas-Cylinder-Trolley.-KE412D-new-copy.jpg 1631w, https://www.kijeka.com/wp-content/uploads/2020/05/2-Wheeler-Single-Gas-Cylinder-Trolley.-KE412D-new-copy-289x300.jpg 289w, https://www.kijeka.com/wp-content/uploads/2020/05/2-Wheeler-Single-Gas-Cylinder-Trolley.-KE412D-new-copy-986x1024.jpg 986w, https://www.kijeka.com/wp-content/uploads/2020/05/2-Wheeler-Single-Gas-Cylinder-Trolley.-KE412D-new-copy-768x798.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/2-Wheeler-Single-Gas-Cylinder-Trolley.-KE412D-new-copy-1479x1536.jpg 1479w, https://www.kijeka.com/wp-content/uploads/2020/05/2-Wheeler-Single-Gas-Cylinder-Trolley.-KE412D-new-copy-70x73.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/2-Wheeler-Single-Gas-Cylinder-Trolley.-KE412D-new-copy-270x280.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/2-Wheeler-Single-Gas-Cylinder-Trolley.-KE412D-new-copy-370x384.jpg 370w, https://www.kijeka.com/wp-content/uploads/2020/05/2-Wheeler-Single-Gas-Cylinder-Trolley.-KE412D-new-copy-1170x1215.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/elevated-steel-box-cart/",
                "name": "Elevated Steel Box Cart",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Steel Bulk Carts Feature a Raised Platform that Eases Physical Strain!</li>\n</ul>\n<ul>\n<li>Elevated 20\u2033 high platform\u00a0reduces lifting effort to help prevent back injuries.</li>\n<li>All welded steel with 20\u2033H\u00a0solid steel\u00a0metal sides.</li>\n<li>Comfortable push handle.</li>\n<li>Rolls easily 2 swivel and 2 rigid.</li>\n<li>Durable Powder coat finish Or Paint</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Elevated Steel Box Cart.</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"198\">Available Capacity</td>\n<td width=\"324\">Up to 500 kgs.</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Top Platform Size</td>\n<td width=\"324\">48\u201d Length X 24\u201d Width x 38\u201d Height From Ground\n<p>48\u201d Length X 36\u201d Width x 38\u201d Height From Ground</p></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Special Top Platform Size/ Sider Height/ Height From Ground</strong></td>\n<td width=\"324\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"198\">Wheel Option</td>\n<td width=\"324\">UHMW-PE, Nylon, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Elevated-Steel-Box-Cart.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Elevated-Steel-Box-Cart.png 181w, https://www.kijeka.com/wp-content/uploads/2017/10/Elevated-Steel-Box-Cart-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/10/Elevated-Steel-Box-Cart-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/gas-cylinder-forklift-storage-transport-pallet/",
                "name": "Gas Cylinder Forklift Storage & Transport Pallet",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Transport multiple gas cylinders securely with a forklift using these end-load oriented pallets.</li>\n<li>Heavy duty pallet with forklift skids. Made of box section with a strong steel base with checker plate. Rachet straps are mounted to the framework for securing bottles and cylinders.</li>\n</ul>\n<p>Product Specifications:</p>\n<ul>\n<li><strong>Dimensions</strong>: H1000 x W1020 x D1000 mm</li>\n<li><strong>Fork Pocket Dimensions</strong>: H70 x W195 mm</li>\n<li><strong>Deck sizes internal (WxD):</strong>\n<ul>\n<li><strong>Front\u00a0</strong>940x670mm</li>\n<li><strong>Rear</strong>: 940x270mm.</li>\n</ul>\n</li>\n<li><strong>Max Load: </strong>1000 KG</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Storage-Transport-Pallet_Website-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Storage-Transport-Pallet_Website-scaled.jpg 2229w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Storage-Transport-Pallet_Website-261x300.jpg 261w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Storage-Transport-Pallet_Website-892x1024.jpg 892w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Storage-Transport-Pallet_Website-768x882.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Storage-Transport-Pallet_Website-1338x1536.jpg 1338w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Storage-Transport-Pallet_Website-1783x2048.jpg 1783w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Storage-Transport-Pallet_Website-70x80.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Storage-Transport-Pallet_Website-270x310.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Storage-Transport-Pallet_Website-370x425.jpg 370w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Storage-Transport-Pallet_Website-1170x1344.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/gas-cylinder-trucks-for-6-or-4-cylinder/",
                "name": "Gas Cylinder Trucks (For 6 Or 4 Cylinder)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Ideal for Move Bulky Gas Cylinders</li>\n<li>Handle 6 or 4 Gas cylinders of 9 \u00bd\u201d dia on double welded cylinder trucks.</li>\n<li>Having chain with locking arrangements.</li>\n<li>1\u201d Lower Ground Clearance for easy Handling for Bulky Cylinder</li>\n<li>Made out of M.S. Angles, flats, pipes, etc\u2026etc.</li>\n<li>Rolls effortlessly on 2- swivel, 2 rigid heavy duty casters.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"601\">\n<tbody>\n<tr>\n<td width=\"233\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"368\"><strong>Gas Cylinder Trucks (For 6 Or 4 Cylinder).\u00a0</strong></td>\n</tr>\n<tr>\n<td width=\"233\">MOC</td>\n<td width=\"368\">MS Powder Coated Finish Or Paint on MS Structure</td>\n</tr>\n<tr>\n<td width=\"233\">Drive Type</td>\n<td width=\"368\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"233\"><strong>Available Size</strong></td>\n<td width=\"368\"><strong>For 6 Or 4 Cylinder Handling </strong></td>\n</tr>\n<tr>\n<td width=\"233\">Wheel Option</td>\n<td width=\"368\">Nylon, Hard Polymer</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-6-Or-4-Cylinder.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-6-Or-4-Cylinder.jpg 742w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-6-Or-4-Cylinder-265x300.jpg 265w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-6-Or-4-Cylinder-70x79.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-6-Or-4-Cylinder-270x305.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/10/Gas-Cylinder-Trucks-For-6-Or-4-Cylinder-370x418.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/hand-trucks-2/",
                "name": "Hand Carts",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Industrial Duty Hand Truck brings you heavy-duty pipe frame constructed hand truck</li>\n<li>All welded joints and a curved back design with a single pin handle, making it comfortable and convenient; you can control it with one hand.</li>\n<li>These hand trucks can carry 500 kgs and is great to use when you need to move large boxes, kegs, or packages.</li>\n</ul>\n<ul>\n<li>Ideal for boxes, kegs, and packages</li>\n<li><strong><em>Available in different\u00a0 sizes &amp; Designs </em></strong></li>\n</ul>\n<p>\u00a0</p>\n<table width=\"601\">\n<tbody>\n<tr>\n<td width=\"210\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"391\"><strong>Hand Trucks.</strong></td>\n</tr>\n<tr>\n<td width=\"210\">MOC</td>\n<td width=\"391\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"210\">Drive Type</td>\n<td width=\"391\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"210\">Wheel Option</td>\n<td width=\"391\">PU, UHMW-PE, Nylon, Solid Rubber Wheels</td>\n</tr>\n<tr>\n<td width=\"210\">Sizes/ Models</td>\n<td width=\"391\">Different Sizes &amp; Models for Different Applications</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Hand-Cart.-KE408_With-PU-Wheels-2-copy-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Hand-Cart.-KE408_With-PU-Wheels-2-copy-scaled.jpg 1231w, https://www.kijeka.com/wp-content/uploads/2017/10/Hand-Cart.-KE408_With-PU-Wheels-2-copy-144x300.jpg 144w, https://www.kijeka.com/wp-content/uploads/2017/10/Hand-Cart.-KE408_With-PU-Wheels-2-copy-492x1024.jpg 492w, https://www.kijeka.com/wp-content/uploads/2017/10/Hand-Cart.-KE408_With-PU-Wheels-2-copy-768x1598.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/10/Hand-Cart.-KE408_With-PU-Wheels-2-copy-738x1536.jpg 738w, https://www.kijeka.com/wp-content/uploads/2017/10/Hand-Cart.-KE408_With-PU-Wheels-2-copy-985x2048.jpg 985w, https://www.kijeka.com/wp-content/uploads/2017/10/Hand-Cart.-KE408_With-PU-Wheels-2-copy-43x90.jpg 43w, https://www.kijeka.com/wp-content/uploads/2017/10/Hand-Cart.-KE408_With-PU-Wheels-2-copy-168x350.jpg 168w, https://www.kijeka.com/wp-content/uploads/2017/10/Hand-Cart.-KE408_With-PU-Wheels-2-copy-231x480.jpg 231w, https://www.kijeka.com/wp-content/uploads/2017/10/Hand-Cart.-KE408_With-PU-Wheels-2-copy-1170x2434.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2017/10/Hand-Cart.-KE408_With-PU-Wheels-2-copy-270x562.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/hospital-oxygen-cylinder-trolley/",
                "name": "Hospital Oxygen Cylinder Trolley",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>We are Manufacturer, Exporters and Suppliers of Oxygen Cylinder Trolley at competitive prices from India.</strong></li>\n<li>Our Hospital Gas Bottle/Cylinder Trolley loads into a recessed supporting cage ensuring that even if the trolley is dropped the load with stay safe, and retained inside the trolley.</li>\n<li><em><strong>Please note that this unit can be manufactured for your choice of gas bottle size if you have something that is not covered by the standard range.</strong></em></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Hospital-Gas-Bottle-Trolley-small.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Hospital-Gas-Bottle-Trolley-small.jpg 500w, https://www.kijeka.com/wp-content/uploads/2021/04/Hospital-Gas-Bottle-Trolley-small-300x300.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Hospital-Gas-Bottle-Trolley-small-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Hospital-Gas-Bottle-Trolley-small-70x70.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Hospital-Gas-Bottle-Trolley-small-270x270.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Hospital-Gas-Bottle-Trolley-small-370x370.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/Hospital-Gas-Bottle-Trolley-small-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/hospital-gas-cylinder-trolley-2-1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/hospital-gas-cylinder-trolley-2-1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/hospital-gas-cylinder-trolley-2-1-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/cylinder-trolly-1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/cylinder-trolly-1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/cylinder-trolly-1-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/mattress-trolley/",
                "name": "Mattress Trolley",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>For transporting particularly bulky items</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"258\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"264\"><strong>Mattress Trolley.</strong></td>\n</tr>\n<tr>\n<td width=\"258\">MOC</td>\n<td width=\"264\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"258\">Drive Type</td>\n<td width=\"264\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"258\">Available Capacity</td>\n<td width=\"264\">Up to 500 kgs.</td>\n</tr>\n<tr>\n<td width=\"258\">Standard Top Platform Size</td>\n<td width=\"264\">10 Feet Length X 5 Feet\u00a0 Width\n<p>5 Feet Length X 5 Feet\u00a0 Width</p></td>\n</tr>\n<tr>\n<td width=\"258\"><strong>Special Top Platform Size/ Sider Height </strong></td>\n<td width=\"264\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"258\">Wheel Option</td>\n<td width=\"264\">UHMW-PE, Nylon, Pneumatic, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/mattress-trolley3.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/mattress-trolley3.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/10/mattress-trolley3-300x188.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/10/mattress-trolley3-768x482.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/10/mattress-trolley3-70x44.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/10/mattress-trolley3-270x170.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/10/mattress-trolley3-370x232.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/mattress-trolley-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/mattress-trolley-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/10/mattress-trolley-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/mig-welding-machine-cart/",
                "name": "MIG Welding Machine Cart",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/MIG-Welding-Machine-Trolley.-KE412E-MIG-1.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/MIG-Welding-Machine-Trolley.-KE412E-MIG-1.jpg 523w, https://www.kijeka.com/wp-content/uploads/2020/05/MIG-Welding-Machine-Trolley.-KE412E-MIG-1-281x300.jpg 281w, https://www.kijeka.com/wp-content/uploads/2020/05/MIG-Welding-Machine-Trolley.-KE412E-MIG-1-70x75.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/MIG-Welding-Machine-Trolley.-KE412E-MIG-1-270x288.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/MIG-Welding-Machine-Trolley.-KE412E-MIG-1-370x395.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/milk-crate-trolley/",
                "name": "Milk Crate Trolley",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Milk-Pouch-Crate-Trolley-3.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Milk-Pouch-Crate-Trolley-3.jpg 1368w, https://www.kijeka.com/wp-content/uploads/2020/05/Milk-Pouch-Crate-Trolley-3-161x300.jpg 161w, https://www.kijeka.com/wp-content/uploads/2020/05/Milk-Pouch-Crate-Trolley-3-548x1024.jpg 548w, https://www.kijeka.com/wp-content/uploads/2020/05/Milk-Pouch-Crate-Trolley-3-768x1435.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Milk-Pouch-Crate-Trolley-3-822x1536.jpg 822w, https://www.kijeka.com/wp-content/uploads/2020/05/Milk-Pouch-Crate-Trolley-3-1096x2048.jpg 1096w, https://www.kijeka.com/wp-content/uploads/2020/05/Milk-Pouch-Crate-Trolley-3-48x90.jpg 48w, https://www.kijeka.com/wp-content/uploads/2020/05/Milk-Pouch-Crate-Trolley-3-187x350.jpg 187w, https://www.kijeka.com/wp-content/uploads/2020/05/Milk-Pouch-Crate-Trolley-3-257x480.jpg 257w, https://www.kijeka.com/wp-content/uploads/2020/05/Milk-Pouch-Crate-Trolley-3-1170x2186.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2020/05/Milk-Pouch-Crate-Trolley-3-270x504.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/nitrogen-gas-cylinder-cart-4-wheeler/",
                "name": "Nitrogen Gas Cylinder Cart (4-Wheeler)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>All New\u2026 First Time in India \u2013 Tilt Back Cylinder Carts</strong></li>\n<li>This tilt back Cylinder Cart holds one gas cylinder up to 10-inch diameter.</li>\n<li><strong>This durable cylinder hand cart is designed to roll on two 8\u2033 main wheels and has fold-down 3-inch diameter rear casters for safe, convenient transport of medical, industrial and commercial use gases on a 4-wheel base.</strong></li>\n<li>The cart construction is made with heavy steel with a contoured back cradle and includes a chain to secure the cylinders. Swing-down steel carriages allow use of rear swivel casters for additional safety and control which fold up when not needed.</li>\n<li>This cylinder trolley is painted blue and is fully welded</li>\n<li><strong>Made in India Product By \u201cKijeka\u201d</strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New_Big-Size-2-copy-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New_Big-Size-2-copy-scaled.jpg 2083w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New_Big-Size-2-copy-244x300.jpg 244w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New_Big-Size-2-copy-833x1024.jpg 833w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New_Big-Size-2-copy-768x944.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New_Big-Size-2-copy-1250x1536.jpg 1250w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New_Big-Size-2-copy-1666x2048.jpg 1666w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New_Big-Size-2-copy-70x86.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New_Big-Size-2-copy-270x332.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New_Big-Size-2-copy-370x455.jpg 370w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New_Big-Size-2-copy-1170x1438.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/oxygen-lpg-double-gas-cylinder-trolley/",
                "name": "Oxygen-LPG Double Gas Cylinder Trolley",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Oxygen-LPG-Cylinder-Truck.-KE411B.jpeg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Oxygen-LPG-Cylinder-Truck.-KE411B.jpeg 1468w, https://www.kijeka.com/wp-content/uploads/2021/04/Oxygen-LPG-Cylinder-Truck.-KE411B-255x300.jpeg 255w, https://www.kijeka.com/wp-content/uploads/2021/04/Oxygen-LPG-Cylinder-Truck.-KE411B-869x1024.jpeg 869w, https://www.kijeka.com/wp-content/uploads/2021/04/Oxygen-LPG-Cylinder-Truck.-KE411B-768x905.jpeg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/Oxygen-LPG-Cylinder-Truck.-KE411B-1303x1536.jpeg 1303w, https://www.kijeka.com/wp-content/uploads/2021/04/Oxygen-LPG-Cylinder-Truck.-KE411B-70x82.jpeg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Oxygen-LPG-Cylinder-Truck.-KE411B-270x318.jpeg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Oxygen-LPG-Cylinder-Truck.-KE411B-370x436.jpeg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/Oxygen-LPG-Cylinder-Truck.-KE411B-1170x1379.jpeg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/panel-cart/",
                "name": "Panel Cart",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Panel Cart is Versatile enough to carry Large Or small Quantities of Sheet Materials</li>\n<li>Carts are perfect for handling Items such as sheet of panelling, Plywood, Door and Lumber</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"601\">\n<tbody>\n<tr>\n<td width=\"233\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"368\"><strong>Panel Cart.</strong></td>\n</tr>\n<tr>\n<td width=\"233\">MOC</td>\n<td width=\"368\">MS Powder Coated Finish Or Paint on MS Structure</td>\n</tr>\n<tr>\n<td width=\"233\">Drive Type</td>\n<td width=\"368\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"233\">Sizes</td>\n<td width=\"368\">Available as per Customer Requirement</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Panel-Cart.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Panel-Cart.png 352w, https://www.kijeka.com/wp-content/uploads/2017/10/Panel-Cart-300x253.png 300w, https://www.kijeka.com/wp-content/uploads/2017/10/Panel-Cart-270x228.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/plastic-container-trolley/",
                "name": "Plastic Container Trolley",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Move and store Fabrics, Chemicals, and Dyes Etc\u2026</li>\n<li>Container Fitted in MS Trolley Structure</li>\n<li><strong><em>Available in different Container Size </em></strong></li>\n</ul>\n<table width=\"601\">\n<tbody>\n<tr>\n<td width=\"233\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"368\"><strong>Plastic Container Trolley.</strong></td>\n</tr>\n<tr>\n<td width=\"233\">MOC</td>\n<td width=\"368\">MS Powder Coated Finish Or Paint on MS Structure</td>\n</tr>\n<tr>\n<td width=\"233\">Drive Type</td>\n<td width=\"368\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"233\"><strong>Available Size</strong></td>\n<td width=\"368\"><strong>As Per Container Size</strong></td>\n</tr>\n<tr>\n<td width=\"233\">Wheel Option</td>\n<td width=\"368\">Nylon, Hard Polymer</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Plastic-Container-Trolley.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Plastic-Container-Trolley.png 313w, https://www.kijeka.com/wp-content/uploads/2017/10/Plastic-Container-Trolley-300x232.png 300w, https://www.kijeka.com/wp-content/uploads/2017/10/Plastic-Container-Trolley-270x209.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/plastic-platform-trucks-with-foldable-handle/",
                "name": "Plastic Platform Trucks- With Foldable Handle",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Transport Products quickly and easily in commercial, Godown, Office, Warehouse, Building or any industrial applications with our Versatile Platform Truck.</li>\n<li>Tough high impact-resistant plastic Top Platform is virtually maintenance free.</li>\n<li>Industrial grade plastic platform will not rust, dent, chip or discolour</li>\n<li>Maintenance free and easy to clean.</li>\n<li><strong>Adjustable handle for pushing or pulling applications, folds down for storage. </strong></li>\n<li>Trolley rolls smoothly on 2- Swivel &amp; 2- Fix Polyurethane Casters</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Plastic Platform Truks-With Foldable Handle</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\"><strong>Heavily Reinforced Plastic &amp; Steel</strong></td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"198\">Available Capacity</td>\n<td width=\"324\">300 kgs&amp; 150 Kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Top Platform Size</td>\n<td width=\"324\"><strong>900 mm Length X 600 mm Width </strong>\n<p><strong>730 mm Length X\u00a0 490 mm Width</strong></p></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Plastic-Platform-Truck-With-Folding-Handle.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Plastic-Platform-Truck-With-Folding-Handle.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/07/Plastic-Platform-Truck-With-Folding-Handle-300x242.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/07/Plastic-Platform-Truck-With-Folding-Handle-768x618.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/07/Plastic-Platform-Truck-With-Folding-Handle-70x56.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/07/Plastic-Platform-Truck-With-Folding-Handle-270x217.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/07/Plastic-Platform-Truck-With-Folding-Handle-370x298.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Plastic-Platform-Truck-With-Folding-Handle1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Plastic-Platform-Truck-With-Folding-Handle1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/07/Plastic-Platform-Truck-With-Folding-Handle1-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/platform-truck-with-pneumatic-wheels/",
                "name": "Platform Truck- With Pneumatic Wheels",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Turntable platform trucks with steel deck</li>\n<li>Efficiently transport packages, boxes, supplies, parts for assembly operations, electronic parts transfer and more. Easy handling, easy rolling.</li>\n</ul>\n<ul>\n<li>Available with Pneumatic Air Filled,</li>\n<li>Smooth rolling\u00a0on Heavy duty Pneumatic (Air filled) Or Solid Rubber(Puncture-Proof)</li>\n</ul>\n<p>Wheels- 04 Nos.</p>\n<ul>\n<li>Powder coat finish Or Paint.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"306\"><strong>Platform Truck-With Pneumatic Wheels.</strong></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Top platform </strong></td>\n<td width=\"306\"><strong>All Side 1\u201d Deep Lip Platform </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Available Capacity</td>\n<td width=\"306\">Up to 2000 kgs.</td>\n</tr>\n<tr>\n<td width=\"216\">Standard Top Platform Size</td>\n<td width=\"306\">48\u201d Length X 24\u201d Width\n<p>48\u201d Length X 36\u201d Width</p>\n<p>60\u201d Length X 36\u201d Width</p>\n<p>60\u201d Length X 48\u201d Width</p></td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Special Top Platform Size</strong></td>\n<td width=\"306\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">UHMW-PE, Nylon, Pneumatic, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-With-Pneumatic-Wheels.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-With-Pneumatic-Wheels.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-With-Pneumatic-Wheels-300x282.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-With-Pneumatic-Wheels-768x721.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-With-Pneumatic-Wheels-70x66.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-With-Pneumatic-Wheels-270x254.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-With-Pneumatic-Wheels-370x347.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/platform-truck-with-pneumatic-wheels-12-steel-sheet-sider-2/",
                "name": "Platform Truck- With Pneumatic Wheels (12\u201d Steel Sheet Sider)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>This Pneumatic Wheel Steel Deck Side Wagon Truck Cart features a solid 12\u201d steel Siders</li>\n<li>Sides that allows for additional carrying capacity.</li>\n<li>Having Turntable Device for Smooth Movement</li>\n<li>Efficiently transport packages, boxes, supplies, parts for assembly operations, electronic parts transfer and more. Easy handling, easy rolling.</li>\n</ul>\n<ul>\n<li>Smooth rolling\u00a0on Heavy duty Pneumatic (Air filled) Or Solid Rubber(Puncture-Proof)</li>\n</ul>\n<p>Wheels- 04 Nos.</p>\n<ul>\n<li>Powder coat finish Or Paint</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"306\"><strong>Platform Truck- With Pneumatic Wheels\u00a0</strong><strong style=\"font-family: inherit; font-size: inherit;\">(12\u201d Steel Sheet Sider).</strong></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Top platform </strong></td>\n<td width=\"306\"><strong>All Side 12\u201d Siders </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Available Capacity</td>\n<td width=\"306\">Up to 2000 kgs.</td>\n</tr>\n<tr>\n<td width=\"216\">Standard Top Platform Size</td>\n<td width=\"306\">48\u201d Length X 24\u201d Width x 12\u201d Sider\n<p>48\u201d Length X 36\u201d Width x 12\u201d Sider</p>\n<p>60\u201d Length X 36\u201d Width x 12\u201d Sider</p>\n<p>60\u201d Length X 48\u201d Width x 12\u201d Sider</p></td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Special Top Platform Size/ Sider Height </strong></td>\n<td width=\"306\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">UHMW-PE, Nylon, Pneumatic, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Platform-Truck-with-Pneumatic-Wheels-12-inch-Sider.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Platform-Truck-with-Pneumatic-Wheels-12-inch-Sider.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/10/Platform-Truck-with-Pneumatic-Wheels-12-inch-Sider-300x211.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/10/Platform-Truck-with-Pneumatic-Wheels-12-inch-Sider-768x540.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/10/Platform-Truck-with-Pneumatic-Wheels-12-inch-Sider-70x49.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/10/Platform-Truck-with-Pneumatic-Wheels-12-inch-Sider-270x190.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/10/Platform-Truck-with-Pneumatic-Wheels-12-inch-Sider-370x260.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/platform-truck-with-pneumatic-wheels-cage-type/",
                "name": "Platform Truck- With Pneumatic Wheels (Cage Type)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>This Pneumatic Wheel Steel Deck Side Wagon Truck Cart features a <strong>solid 30\u201d steel </strong><strong>slat</strong><strong>Siders.</strong></li>\n<li>Steel Cage that allows for additional carrying capacity with Safe Movement of \u00a0material.</li>\n<li><strong>Lengthwise Single Side open able gate for easy Loading unloading of Material.</strong></li>\n<li><strong>Having Turntable Device for Smooth Movement.</strong></li>\n<li>Efficiently transport packages, boxes, supplies, parts for assembly operations, electronic parts transfer and more. Easy handling, easy rolling.</li>\n</ul>\n<ul>\n<li>Smooth rolling\u00a0on Heavy duty Pneumatic (Air filled) Or Solid Rubber(Puncture-Proof)</li>\n</ul>\n<p>Wheels- 04 Nos.</p>\n<ul>\n<li>Powder coat finish Or Paint.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"306\"><strong>Platform Truck- With Pneumatic Wheels </strong>\n<p><strong>(Cage Type).</strong></p></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Top platform </strong></td>\n<td width=\"306\"><strong>All Side 30\u201d \u00a0Steel Slat Siders</strong></td>\n</tr>\n<tr>\n<td width=\"216\">Available Capacity</td>\n<td width=\"306\">Up to 2000 kgs.</td>\n</tr>\n<tr>\n<td width=\"216\">Standard Top Platform Size</td>\n<td width=\"306\">48\u201d Length X 24\u201d Width x 30\u201d Sider\n<p>48\u201d Length X 36\u201d Width x 30\u201d Sider</p>\n<p>60\u201d Length X 36\u201d Width x 30\u201d Sider</p>\n<p>60\u201d Length X 48\u201d Width x 30\u201d Sider</p></td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Special Top Platform Size/ Sider Height </strong></td>\n<td width=\"306\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">UHMW-PE, Nylon, Pneumatic, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Pneuamtic-Wheels-Cage-Type2.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Pneuamtic-Wheels-Cage-Type2.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Pneuamtic-Wheels-Cage-Type2-300x229.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Pneuamtic-Wheels-Cage-Type2-768x587.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Pneuamtic-Wheels-Cage-Type2-70x53.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Pneuamtic-Wheels-Cage-Type2-270x206.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Pneuamtic-Wheels-Cage-Type2-370x283.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Pneuamtic-Wheels-Cage-Type-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Pneuamtic-Wheels-Cage-Type-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Pneuamtic-Wheels-Cage-Type-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/platform-trucks-2/",
                "name": "Platform Trucks",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>An all-purpose truck to save time and money.</li>\n<li>All welded construction ensures a super strength truck</li>\n<li>Trolley Made out of MS Sheets, angles, flats, pipes, etc\u2026etc.</li>\n<li>Platform trolley with convenient tubular push handle</li>\n<li>Rolls effortlessly on 2- swivel, 2 rigid heavy duty casters.</li>\n<li>Duly powder coated and ready for use</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Platform Truks.</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"198\">Available Capacity</td>\n<td width=\"324\">Up to 2000 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Top Platform Size</td>\n<td width=\"324\">48\u201d Length X 36\u201d Width\n<p>60\u201d Length X 36\u201d Width</p>\n<p>60\u201d Length X 48\u201d Width</p></td>\n</tr>\n<tr>\n<td width=\"198\">Special Top Platform Size</td>\n<td width=\"324\">As Per your Requirement</td>\n</tr>\n<tr>\n<td width=\"198\">Wheel Option</td>\n<td width=\"324\">UHMW-PE, Nylon, Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-300x242.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-768x619.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-70x56.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-270x218.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-370x298.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-150x135.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/platform-trucks-for-plastic-crates-handling/",
                "name": "Platform Trucks- For Plastic Crates Handling",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Platform Truck with MS Frame Structure for Handling Crates or Plastic Containers.</li>\n<li>All welded construction ensures a super strength truck.</li>\n<li>Trolley Made out of MS Sheets, angles, flats, pipes, etc\u2026etc.</li>\n<li>Rolls effortlessly on 2- swivel, 2 rigid heavy duty casters.</li>\n<li>Duly powder coated and ready for use.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"520\">\n<tbody>\n<tr>\n<td width=\"197\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"323\"><strong>Platform Trucks- For Plastic Crates Handling</strong></td>\n</tr>\n<tr>\n<td width=\"197\">MOC</td>\n<td width=\"323\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"197\">Drive Type</td>\n<td width=\"323\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"197\">Available Capacity</td>\n<td width=\"323\">Up to 500 kgs Or As per your requirement</td>\n</tr>\n<tr>\n<td width=\"197\"><strong>Standard Top Frame Size</strong></td>\n<td width=\"323\"><strong>810 mm Length X 610mm Width </strong></td>\n</tr>\n<tr>\n<td width=\"197\"><strong>Special\u00a0 Top Frame Size</strong></td>\n<td width=\"323\"><strong>As Per Plastic Crates Outer Dimension\u00a0 </strong></td>\n</tr>\n<tr>\n<td width=\"197\">Wheel Option</td>\n<td width=\"323\">UHMW-PE, Nylon, Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-For-Plastic-Crates-Handling.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-For-Plastic-Crates-Handling.png 295w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-For-Plastic-Crates-Handling-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-For-Plastic-Crates-Handling-270x270.png 270w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-For-Plastic-Crates-Handling-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/platform-trucks-lower-side-with-turn-table-device/",
                "name": "Platform Trucks- Lower Side with Turn Table Device",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Perfect for heavy weight transportation around the warehouse, plant or office.</li>\n<li><strong>Wheel steering (turn table device) for effortless movement.</strong></li>\n<li>All welded construction ensures a super strength truck</li>\n<li>Trolley Made out of MS Sheets, angles, flats, pipes, etc\u2026etc.</li>\n<li>Platform trolley with convenient tubular Pull handle.</li>\n<li>Rolls effortlessly on 4- heavy duty wheels.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Platform Trucks- With Turn Table Device.</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"198\">Available Capacity</td>\n<td width=\"324\">Up to 5000 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Top Platform Size</td>\n<td width=\"324\">48\u201d Length X 36\u201d Width\n<p>60\u201d Length X 36\u201d Width</p>\n<p>60\u201d Length X 48\u201d Width</p>\n<p>72\u201d Length X 48\u201d Width</p>\n<p>72\u201d Length X 60\u201d Width</p></td>\n</tr>\n<tr>\n<td width=\"198\">Special Top Platform Size</td>\n<td width=\"324\">As Per your Requirement</td>\n</tr>\n<tr>\n<td width=\"198\">Wheel Option</td>\n<td width=\"324\">UHMW-PE, Nylon, Pneumatic, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-Lower-Sider-With-Turntable-Device.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-Lower-Sider-With-Turntable-Device.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-Lower-Sider-With-Turntable-Device-300x269.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-Lower-Sider-With-Turntable-Device-768x690.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-Lower-Sider-With-Turntable-Device-70x63.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-Lower-Sider-With-Turntable-Device-270x242.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-Lower-Sider-With-Turntable-Device-370x332.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/platform-trucks-towable-trailers/",
                "name": "Platform Trucks- Towable Trailers",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Perfect for heavy weight transportation around the warehouse, plant</li>\n<li><strong>Wheel steering (turn table device) for effortless movement.</strong></li>\n<li>All welded construction ensures a super strength truck</li>\n<li>Trolley Made out of MS Sheets, angles, flats, pipes, etc\u2026etc.</li>\n<li>Platform trolley with convenient tubular Pull- Towing handle.</li>\n<li>Rolls effortlessly on 4- heavy duty wheels.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\">\n<p style=\"text-align: left;\"><strong>Platform Trucks- Towable Trailers</strong></p>\n</td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"198\">Available Capacity</td>\n<td width=\"324\">Up to 5000 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Top Platform Size</td>\n<td width=\"324\">96\u201d Length X 48\u201d Width\n<p>72\u201d Length X 36\u201d Width</p></td>\n</tr>\n<tr>\n<td width=\"198\">Special Top Platform Size</td>\n<td width=\"324\">As Per your Requirement</td>\n</tr>\n<tr>\n<td width=\"198\">Wheel Option</td>\n<td width=\"324\">UHMW-PE, Solid Rubber, Mild Steel Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-Towable-Trailers.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-Towable-Trailers.png 510w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-Towable-Trailers-300x172.png 300w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-Towable-Trailers-270x155.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/platform-trucks-with-adjustable-working-platform/",
                "name": "Platform Trucks- With Adjustable Working Platform",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Comfortable height to minimize bending and reduce back strain.</li>\n<li><strong>Top Platform Adjustable height 24\u2033 \u2013 34\u2033</strong></li>\n<li>All welded construction ensures a super strength truck</li>\n<li>Trolley Made out of MS Sheets, angles, flats, pipes, etc\u2026etc.</li>\n<li>Rolls effortlessly on 2- swivel, 2 rigid heavy duty casters.</li>\n<li>Duly powder coated and ready for use</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Platform Trucks- With Adjustable Working</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"198\">Available Capacity</td>\n<td width=\"324\">Up to 1000 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Top Platform Size</td>\n<td width=\"324\">48\u201d Length X 24\u201d Width\n<p>48\u201d Length X 30\u201d Width</p>\n<p>60\u201d Length X 24\u201d Width</p>\n<p>60\u201d Length X 30\u201d Width</p></td>\n</tr>\n<tr>\n<td width=\"198\">Special Top Platform Size</td>\n<td width=\"324\">As Per your Requirement</td>\n</tr>\n<tr>\n<td width=\"198\">Wheel Option</td>\n<td width=\"324\">UHMW-PE, Nylon, Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Adjustable-Working-Platform.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Adjustable-Working-Platform.png 451w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Adjustable-Working-Platform-300x210.png 300w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Adjustable-Working-Platform-270x189.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/platform-trucks-with-dual-handle/",
                "name": "Platform Trucks- With Dual Handle",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>An all-purpose truck to save time and money.</li>\n<li>All welded construction ensures a super strength truck</li>\n<li>Trolley Made out of MS Sheets, angles, flats, pipes, etc\u2026etc.</li>\n<li>Platform trolley with Dual convenient tubular Push-Pull handles</li>\n<li>Rolls effortlessly on 4- swivel, 2 rigid heavy duty casters.</li>\n<li>Duly powder coated and ready for use</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Platform Truks.</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"198\">Available Capacity</td>\n<td width=\"324\">Up to 2000 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Top Platform Size</td>\n<td width=\"324\">48\u201d Length X 36\u201d Width\n<p>60\u201d Length X 36\u201d Width</p>\n<p>60\u201d Length X 48\u201d Width</p></td>\n</tr>\n<tr>\n<td width=\"198\">Special Top Platform Size</td>\n<td width=\"324\">As Per your Requirement</td>\n</tr>\n<tr>\n<td width=\"198\">Wheel Option</td>\n<td width=\"324\">UHMW-PE, Nylon, Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-With-Dual-Handle.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/platform-trucks-with-turn-table-device/",
                "name": "Platform Trucks- With Turn Table Device",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Perfect for heavy weight transportation around the warehouse, plant or office.</li>\n<li><strong>Wheel steering (turn table device) for effortless movement.</strong></li>\n<li>All welded construction ensures a super strength truck</li>\n<li>Trolley Made out of MS Sheets, angles, flats, pipes, etc\u2026etc.</li>\n<li>Platform trolley with convenient tubular Pull handle.</li>\n<li>Rolls effortlessly on 4- heavy duty wheels.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"564\">\n<tbody>\n<tr>\n<td style=\"text-align: center;\" width=\"222\"><strong>Model</strong></td>\n<td width=\"342\"><strong>Platform Trucks- With Turn Table Device. </strong></td>\n</tr>\n<tr>\n<td width=\"222\">MOC</td>\n<td width=\"342\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"222\">Drive Type</td>\n<td width=\"342\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"222\">Available Capacity</td>\n<td width=\"342\">Up to 5000 kgs</td>\n</tr>\n<tr>\n<td width=\"222\">Standard Top Platform Size</td>\n<td width=\"342\">48\u201d Length X 36\u201d Width\n<p>60\u201d Length X 36\u201d Width</p>\n<p>60\u201d Length X 48\u201d Width</p>\n<p>72\u201d Length X 48\u201d Width</p>\n<p>72\u201d Length X 60\u201d Width</p></td>\n</tr>\n<tr>\n<td width=\"222\">Special Top Platform Size</td>\n<td width=\"342\">As Per your Requirement</td>\n</tr>\n<tr>\n<td width=\"222\">Wheel Option</td>\n<td width=\"342\">UHMW-PE, Nylon, Pneumatic, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-with-Turntable-Device.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-with-Turntable-Device.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-with-Turntable-Device-300x218.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-with-Turntable-Device-768x559.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-with-Turntable-Device-70x51.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-with-Turntable-Device-270x197.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Trucks-with-Turntable-Device-370x269.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/platform-trucks-with-deep-lip-platform/",
                "name": "Platform Trucks-With Deep Lip Platform",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><b>Deep Lip Steel Platform Trucks are used for Retaining Cargo during Commercial or Industrial Transport Applications.</b></li>\n<li>Deep 6\u201d Wall Steel Platform Trucks are made of solid all-welded heavy gauge steel, and feature powder coated finished frames</li>\n<li><strong>Wheel steering (turn table device) for effortless movement.</strong></li>\n<li>Trolley Made out of MS Sheets, angles, flats, pipes, etc\u2026etc.</li>\n<li>Platform trolley with convenient tubular Pull handle.</li>\n<li>Rolls effortlessly on 4- heavy duty wheels.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td style=\"text-align: center;\" width=\"198\"><strong>Model</strong></td>\n<td width=\"324\"><strong>Platform Trucks- With Deep Lip Platform</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"198\">Deep Lip</td>\n<td width=\"324\">6\u201d Standard Or As per your requirement</td>\n</tr>\n<tr>\n<td width=\"198\">Available Capacity</td>\n<td width=\"324\">Up to 5000 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Top Platform Size</td>\n<td width=\"324\">36\u201d Length X 24\u201d Width\n<p>48\u201d Length X 24\u201d Width</p>\n<p>60\u201d Length X 30\u201d Width</p></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Special Top Platform Size </strong></td>\n<td width=\"324\"><strong>As Per your Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"198\">Wheel Option</td>\n<td width=\"324\">UHMW-PE, Nylon, Pneumatic, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-with-Deep-lip-Platform.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-with-Deep-lip-Platform.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-with-Deep-lip-Platform-300x269.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-with-Deep-lip-Platform-768x690.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-with-Deep-lip-Platform-70x63.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-with-Deep-lip-Platform-270x242.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/07/Platform-Truck-with-Deep-lip-Platform-370x332.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/portable-shelf-truck/",
                "name": "Portable Shelf Truck",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Efficiently transport bulky packages, boxes, supplies, parts for assembly operations, electronic parts transfer and more. Easy handling, easy rolling.</li>\n<li>Built for heavy loads.</li>\n<li>Frame is made from steel tubing, rods on sides and back.</li>\n<li>14\u2033 Or as per required clearance between shelves.</li>\n<li>Smooth rolling\u00a06\u2033 x 2\u2033 casters, 2 swivel, 2 rigid.</li>\n<li>powder coat finish Or Paint.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"306\"><strong>Portable Shelf Truck.</strong></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"216\">Sider</td>\n<td width=\"306\">3-Sided Covered</td>\n</tr>\n<tr>\n<td width=\"216\">Available Capacity</td>\n<td width=\"306\">Up to 1000 kgs.</td>\n</tr>\n<tr>\n<td width=\"216\">Standard Top Platform Size</td>\n<td width=\"306\">36\u201d Length X 24\u201d Width X 58\u201d Sider\n<p>48\u201d Length X 24\u201d Width X 58\u201d Sider</p>\n<p>60\u201d Length X 30\u201d Width X 58\u201d Sider</p>\n<p>72\u201d Length X 30\u201d Width X 58\u201d Sider</p>\n<p>\u00a0</p></td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Special Platform Size/ Sider Height/</strong>\n<p><strong>Clearance between Shelves/ Number of Shelves </strong></p></td>\n<td width=\"306\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">UHMW-PE, Nylon, Pneumatic, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Portable-Shelf-Truck.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/07/Portable-Shelf-Truck.png 378w, https://www.kijeka.com/wp-content/uploads/2017/07/Portable-Shelf-Truck-285x300.png 285w, https://www.kijeka.com/wp-content/uploads/2017/07/Portable-Shelf-Truck-270x284.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/propane-gas-cylinder-cart/",
                "name": "Propane Gas Cylinder Cart",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Propane cylinder trolley with tubular steel powder coated frame designed to safely manoeuvre 47kg propane cylinders.</li>\n<li>3 Wheeler Trolley</li>\n<li>Having chain with locking arrangements.</li>\n<li>Made out of M.S. Angles, flats, pipes, etc\u2026etc.</li>\n<li>Rolls effortlessly on 3 Wheels</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"601\">\n<tbody>\n<tr>\n<td width=\"233\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"368\"><strong>Propane Gas Cylinder Trucks. </strong></td>\n</tr>\n<tr>\n<td width=\"233\">MOC</td>\n<td width=\"368\">MS Powder Coated Finish Or Paint on MS Structure</td>\n</tr>\n<tr>\n<td width=\"233\">Drive Type</td>\n<td width=\"368\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"233\">Wheel Option</td>\n<td width=\"368\">Nylon, Hard Polymer, Rubber</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Propane-Gas-Cylinder-Trucks.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/shelf-cart-tray-trolley/",
                "name": "Shelf Cart (Tray Trolley)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Ideal for heavy duty steel cart applications.</li>\n<li>Suitable\u00a0for everyday use in\u00a0offices, factories, warehouses, schools, universities and hospitals.</li>\n<li>Made out of MS Sheets, angles, flats, pipes, etc\u2026etc.</li>\n<li>Heavy-duty all welded steel construction with shelves (front to rear).</li>\n<li>Tray trolley with convenient tubular push handle.</li>\n<li>Extra mobility thanks to 2- swivel, 2 rigid heavy duty casters.</li>\n<li>Durable Powder coat finish Or Paint</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"306\"><strong>Shelf Cart (Tray Trolley).</strong></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"216\">Available Capacity</td>\n<td width=\"306\">Up to 500 kgs.</td>\n</tr>\n<tr>\n<td width=\"216\">Standard Top Platform Size</td>\n<td width=\"306\">36\u201d Length X 24\u201d Width</td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Special \u00a0Tray \u00a0Size/ Number of Compartment- Shelves </strong></td>\n<td width=\"306\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">UHMW-PE, Nylon, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Shelf-Cart-Tray-Trolley.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/single-cylinder-lifting-trolley/",
                "name": "Single Cylinder Lifting Trolley",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Designed for lifting or wheeling cylinders around the floor</strong></li>\n<li>Cylinder lifting trolley to carry either oxygen/acetylene gas cylinders.</li>\n<li>This trolley comes with top and bottom cylinder restraints also supplied</li>\n<li>The cylinder trolley is available with steel link retaining chains to the top and bottom for safe cylinder securement\u00a0.</li>\n<li>50mm diameter lifting eye fitted on top of the unit for easy attachment to any overhead<br/>\nlifting gear</li>\n<li>Duly paint or Powder coated finished.. Made in India Product</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Single-Cylinder-Lifting-Trolley-copy.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Single-Cylinder-Lifting-Trolley-copy.jpg 288w, https://www.kijeka.com/wp-content/uploads/2020/05/Single-Cylinder-Lifting-Trolley-copy-105x300.jpg 105w, https://www.kijeka.com/wp-content/uploads/2020/05/Single-Cylinder-Lifting-Trolley-copy-32x90.jpg 32w, https://www.kijeka.com/wp-content/uploads/2020/05/Single-Cylinder-Lifting-Trolley-copy-123x350.jpg 123w, https://www.kijeka.com/wp-content/uploads/2020/05/Single-Cylinder-Lifting-Trolley-copy-169x480.jpg 169w, https://www.kijeka.com/wp-content/uploads/2020/05/Single-Cylinder-Lifting-Trolley-copy-270x769.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/single-gas-cylinder-cart/",
                "name": "Single Gas Cylinder Cart (2-Wheeler)",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Single-Gas-Cylinder-Trucks.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Single-Gas-Cylinder-Trucks.png 133w, https://www.kijeka.com/wp-content/uploads/2017/10/Single-Gas-Cylinder-Trucks-120x300.png 120w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/3-wheeler-single-gas-cylinder-cart/",
                "name": "Single Gas Cylinder Cart (3-Wheeler)",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/3-Wheeler-Single-Gas-Cylinder-Trucks.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/3-Wheeler-Single-Gas-Cylinder-Trucks.png 280w, https://www.kijeka.com/wp-content/uploads/2017/10/3-Wheeler-Single-Gas-Cylinder-Trucks-270x190.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/single-gas-cylinder-cart-new/",
                "name": "Single Gas Cylinder Cart (4-Wheeler)",
                "desc": "None",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New-copy-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New-copy-scaled.jpg 1931w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New-copy-226x300.jpg 226w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New-copy-773x1024.jpg 773w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New-copy-768x1018.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New-copy-1159x1536.jpg 1159w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New-copy-1545x2048.jpg 1545w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New-copy-68x90.jpg 68w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New-copy-264x350.jpg 264w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New-copy-362x480.jpg 362w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New-copy-1170x1551.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2020/05/Cylinder-Cart-New-copy-270x358.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/stair-climbing-hand-trucks/",
                "name": "Stair Climbing Hand Trucks",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><b>Steel Stair Climbing Hand Trucks are used for Moving Up and Down Stairs with Heavy Loads.</b></li>\n<li>Capacities are <b>150 kgs</b></li>\n<li>Steel Stair Climbing Hand Trucks are made of steel for long lasting durability and dependability.</li>\n<li>Stair Hand Truck provides two people access for transporting loads up and down stairways or hills.</li>\n<li>Easy grip handles allow comfort. Heavy duty wheels provide mobility.</li>\n<li>Color Or Powder Coating\u00a0 finishes are <b>Blue or Yellow</b>.</li>\n<li><strong>Made in India Product\u00a0</strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Stair-Climbing-Hand-Trucks_Website--scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Stair-Climbing-Hand-Trucks_Website--scaled.jpg 1581w, https://www.kijeka.com/wp-content/uploads/2020/05/Stair-Climbing-Hand-Trucks_Website--185x300.jpg 185w, https://www.kijeka.com/wp-content/uploads/2020/05/Stair-Climbing-Hand-Trucks_Website--632x1024.jpg 632w, https://www.kijeka.com/wp-content/uploads/2020/05/Stair-Climbing-Hand-Trucks_Website--768x1244.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Stair-Climbing-Hand-Trucks_Website--949x1536.jpg 949w, https://www.kijeka.com/wp-content/uploads/2020/05/Stair-Climbing-Hand-Trucks_Website--1265x2048.jpg 1265w, https://www.kijeka.com/wp-content/uploads/2020/05/Stair-Climbing-Hand-Trucks_Website--56x90.jpg 56w, https://www.kijeka.com/wp-content/uploads/2020/05/Stair-Climbing-Hand-Trucks_Website--216x350.jpg 216w, https://www.kijeka.com/wp-content/uploads/2020/05/Stair-Climbing-Hand-Trucks_Website--296x480.jpg 296w, https://www.kijeka.com/wp-content/uploads/2020/05/Stair-Climbing-Hand-Trucks_Website--1170x1895.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2020/05/Stair-Climbing-Hand-Trucks_Website--270x437.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/steel-box-cart/",
                "name": "Steel Box Cart",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Efficiently transport packages, boxes, supplies, parts for assembly operations, electronic parts transfer and more. Easy handling, easy rolling.</li>\n</ul>\n<ul>\n<li>Solid wall box truck with steel deck and 12\u201d sides can transport loads up to 1000 Kgs\u00a0 depending on model</li>\n<li>Manoeuvres easily with two rigid and two swivel casters. Tubular steel handle provides comfortable handling</li>\n<li><strong>Some models include extra features, such as a drop gate for side access or a lockable lid to secure contents</strong></li>\n</ul>\n<ul>\n<li><strong>Having Turntable Device for Smooth Movement </strong></li>\n<li>Steel sider that allows for additional carrying capacity with Safe Movement of \u00a0material</li>\n<li>Powder coat finish Or Paint</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"306\"><strong>Steel Box Cart.</strong></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push-Pull Type</td>\n</tr>\n<tr>\n<td width=\"216\">Available Capacity</td>\n<td width=\"306\">Up to 1000 kgs.</td>\n</tr>\n<tr>\n<td width=\"216\">Standard Top Platform Size</td>\n<td width=\"306\">48\u201d Length X 24\u201d Width x 12\u201d Sider\n<p>48\u201d Length X 36\u201d Width x 12\u201d Sider</p>\n<p>60\u201d Length X 36\u201d Width x 12\u201d Sider</p>\n<p>60\u201d Length X 48\u201d Width x 12\u201d Sider</p></td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Special Top Platform Size/ Sider Height </strong></td>\n<td width=\"306\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">UHMW-PE, Nylon, Pneumatic, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart-255x300.jpg 255w, https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart-768x902.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart-871x1024.jpg 871w, https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart-70x82.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart-270x317.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart-370x435.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/steel-box-cart-4-side-solid-sider/",
                "name": "Steel Box Cart- 4 Side Solid Sider",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Bulk storage and transport trucks have 24\u201d interior height.</li>\n<li>All welded steel with 24\u2033H\u00a0solid steel\u00a0metal sides.</li>\n<li>Comfortable push handle.</li>\n<li>Rolls easily 2 swivel and 2 rigid.</li>\n<li>Durable Powder coat finish Or Paint</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td style=\"text-align: center;\" width=\"216\"><strong>Model</strong></td>\n<td width=\"306\"><strong>Steel Box Cart- 4 Side Solid Sider.</strong></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"216\">Available Capacity</td>\n<td width=\"306\">Up to 1000 kgs.</td>\n</tr>\n<tr>\n<td width=\"216\">Standard Top Platform Size</td>\n<td width=\"306\">36\u201d Length X 24\u201d Width x 24\u201d Deep\n<p>48\u201d Length X 36\u201d Width x 24\u201d Deep</p>\n<p>\u00a0</p></td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Special Top Platform Size/ Sider Height/ Height From Ground</strong></td>\n<td width=\"306\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">UHMW-PE, Nylon, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart-4-Side-Solid-Sider.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart-4-Side-Solid-Sider.png 295w, https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart-4-Side-Solid-Sider-270x190.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/steel-box-cart-with-hinged-lid/",
                "name": "Steel Box Cart- With Hinged Lid",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Bulk storage and transport trucks have 24\u201d interior height. Hinged top cover has</li>\n</ul>\n<p>Padlock hasp for security.</p>\n<ul>\n<li>All welded steel with 24\u2033H\u00a0solid steel\u00a0metal sides.</li>\n<li>Comfortable push handle.</li>\n<li>Rolls easily 2 swivel and 2 rigid.</li>\n<li>Durable Powder coat finish Or Paint</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"306\"><strong>Steel Box Cart- With Hinged Lid</strong></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"216\">Available Capacity</td>\n<td width=\"306\">Up to 1000 kgs.</td>\n</tr>\n<tr>\n<td width=\"216\">Standard Top Platform Size</td>\n<td width=\"306\">36\u201d Length X 24\u201d Width x 24\u201d Deep\n<p>48\u201d Length X 36\u201d Width x 24\u201d Deep</p>\n<p>\u00a0</p></td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Special Top Platform Size/ Sider Height/ Height From Ground</strong></td>\n<td width=\"306\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">UHMW-PE, Nylon, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart-With-Hinged-Lid.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart-With-Hinged-Lid.png 269w, https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart-With-Hinged-Lid-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/10/Steel-Box-Cart-With-Hinged-Lid-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/tool-cart/",
                "name": "Tool Cart",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Ideal for component, small part storage and transfer to assembly or production areas. </strong></li>\n<li>Tool Trolley features an auto return ball bearing system, with spring-loaded slides for smooth drawer action even when fully loaded and an increased load capacity of drawers</li>\n<li>Design allows for easier to remove drawers with 100% drawer extension for full access to tools or Parts</li>\n<li>Heavy gauge steel on critical sections of chest, for a stronger longer lasting product.</li>\n<li><strong><em>Available in different sizes &amp; Drawers Option\u00a0 </em></strong></li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"306\"><strong>Tool Cart.</strong></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">PU, UHMW-PE, Nylon, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Tool-Cart-1.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Tool-Cart-1.png 292w, https://www.kijeka.com/wp-content/uploads/2017/10/Tool-Cart-1-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/10/Tool-Cart-1-270x270.png 270w, https://www.kijeka.com/wp-content/uploads/2017/10/Tool-Cart-1-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/traffic-cone-cart/",
                "name": "Traffic Cone Cart",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>This\u00a0<strong>Traffic Cone Cart</strong>\u00a0is used for transporting and storing traffic cones.</li>\n<li>Safely &amp; easily transports traffic cones with little effort</li>\n<li>Constructed of 1\u2033 round heavy-duty 14 gauge steel tubing</li>\n<li>Holds up to 25 standard or reflective cones from 12\u2033 to 28\u2033 in height</li>\n<li>Duly Paint or Powder Coated Finish</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Traffic-Cone-Cart-copy.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Traffic-Cone-Cart-copy.jpg 1692w, https://www.kijeka.com/wp-content/uploads/2020/05/Traffic-Cone-Cart-copy-243x300.jpg 243w, https://www.kijeka.com/wp-content/uploads/2020/05/Traffic-Cone-Cart-copy-828x1024.jpg 828w, https://www.kijeka.com/wp-content/uploads/2020/05/Traffic-Cone-Cart-copy-768x950.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Traffic-Cone-Cart-copy-1242x1536.jpg 1242w, https://www.kijeka.com/wp-content/uploads/2020/05/Traffic-Cone-Cart-copy-1656x2048.jpg 1656w, https://www.kijeka.com/wp-content/uploads/2020/05/Traffic-Cone-Cart-copy-70x87.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Traffic-Cone-Cart-copy-270x334.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Traffic-Cone-Cart-copy-370x458.jpg 370w, https://www.kijeka.com/wp-content/uploads/2020/05/Traffic-Cone-Cart-copy-1170x1447.jpg 1170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/wheel-barrows/",
                "name": "Wheel Barrows",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Wheel Barrows are mainly used to carry waste materials from the public places.</li>\n<li>Besides, wheel barrows are also used in manufacturing plants for carrying basic material as well as finished products.</li>\n<li>Our range of Wheelbarrows has gained wide applauds from the clients for features such as abrasion resistant finish, low maintenance and easy operation.</li>\n<li><strong><em>Available in different sizes &amp; Wheel Option </em></strong></li>\n</ul>\n<p>\u00a0</p>\n<table width=\"577\">\n<tbody>\n<tr>\n<td width=\"186\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"391\"><strong>Wheel Barrows \u00a0</strong></td>\n</tr>\n<tr>\n<td width=\"186\">MOC</td>\n<td width=\"391\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"186\">Drive Type</td>\n<td width=\"391\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"186\">Wheel Option</td>\n<td width=\"391\">Hard Polymer, M.S,\u00a0 CI Rubber Moulded, Pneumatic</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow-all-Type.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow-all-Type.jpg 2480w, https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow-all-Type-300x259.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow-all-Type-1024x884.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow-all-Type-768x663.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow-all-Type-1536x1327.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow-all-Type-2048x1769.jpg 2048w, https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow-all-Type-70x60.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow-all-Type-270x233.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow-all-Type-370x320.jpg 370w, https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow-all-Type-1170x1011.jpg 1170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow.-KE410A_Website-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow.-KE410A_Website-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow.-KE410A_Website-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow.-KE410B-1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow.-KE410B-1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow.-KE410B-1-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow.-KE410D-1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow.-KE410D-1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow.-KE410D-1-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow.-KE410E_Web-Site-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow.-KE410E_Web-Site-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/10/Wheel-Barrow.-KE410E_Web-Site-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/wire-mesh-trolley/",
                "name": "Wire Mesh Trolley",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Mesh construction for open air, see-thru use</li>\n<li>All welded construction for long lasting use.</li>\n<li>Made out of M.S. wire net, Sheets, angles, flats, pipes, etc\u2026etc.</li>\n<li>Extra mobility thanks to 2- swivel, 2 rigid heavy duty casters.</li>\n<li>Durable Powder coat finish Or Paint</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"216\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"306\"><strong>Wire Mesh Trolley.</strong></td>\n</tr>\n<tr>\n<td width=\"216\">MOC</td>\n<td width=\"306\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"216\">Drive Type</td>\n<td width=\"306\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"216\">Available Capacity</td>\n<td width=\"306\">Up to 500 kgs.</td>\n</tr>\n<tr>\n<td width=\"216\">Standard Top Platform Size</td>\n<td width=\"306\">36\u201d Length X 24\u201d Width x 24\u201d Deep\n<p>48\u201d Length X 36\u201d Width x 24\u201d Deep</p></td>\n</tr>\n<tr>\n<td width=\"216\"><strong>Special Top Platform Size/ Sider Height/ Height From Ground</strong></td>\n<td width=\"306\"><strong>As Per Requirement </strong></td>\n</tr>\n<tr>\n<td width=\"216\">Wheel Option</td>\n<td width=\"306\">UHMW-PE, Nylon, Solid Rubber Wheels</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wire-Mesh-Trolley.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wire-Mesh-Trolley.png 171w, https://www.kijeka.com/wp-content/uploads/2017/10/Wire-Mesh-Trolley-170x156.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/wire-reel-cart/",
                "name": "Wire Reel Cart",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Wire Reel Cart is a versatile dispensing system designed to easily transport spooled products at the jobsite.</li>\n<li>Wire Reel Cart is constructed from welded steel tubing which offers 150 kgs capacity of spools up to 16\u2033 diameter x 17\u2033 wide.</li>\n<li>Wire Reel Cart features Five Solid-steel spool bars, zinc plated, that are corrosion resistant</li>\n<li>Trolley Fitted On 2 Wheels Nylon/ Rubber\u00a0 wheels for Easy movement</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"601\">\n<tbody>\n<tr>\n<td width=\"233\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"368\"><strong>Wire Reel Cart.</strong></td>\n</tr>\n<tr>\n<td width=\"233\">MOC</td>\n<td width=\"368\">MS Powder Coated Finish Or Paint on MS Structure</td>\n</tr>\n<tr>\n<td width=\"233\">Drive Type</td>\n<td width=\"368\">Manual Push Type</td>\n</tr>\n<tr>\n<td width=\"233\">Size</td>\n<td width=\"368\">43\u2033 x 24\u2033 x 22\u2033.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wire-Reel-Cart.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/10/Wire-Reel-Cart.png 206w, https://www.kijeka.com/wp-content/uploads/2017/10/Wire-Reel-Cart-183x300.png 183w"
                    ]
                ]
            }
        ],
        "Order Picker Trucks": [
            {
                "link": "https://www.kijeka.com/product/self-propelled-stock-order-picker/",
                "name": "Self-propelled Stock Order Picker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>The light weight and manoeuvrability make it convenient to use in supermarket, warehouse, Industries</li>\n<li>Order picker is mainly used to pick up cargo from rack. Operator can control moving, lifting and turning when stand on the platform, which highly improved the working\u2026</li>\n<li>Zero-turn radius and compact design provide access in and around confined work areas.</li>\n<li>On-board diagnostic help operators troubleshoot on the fly and make adjustments in the field to maximize uptime.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"98%\">\n<tbody>\n<tr>\n<td width=\"23%\"><strong>Model</strong></td>\n<td colspan=\"6\" width=\"76%\">\n<strong>Self-propelled Stock Order Picker</strong>\n</td>\n</tr>\n<tr>\n<td>Platform height(mm)</td>\n<td>2000</td>\n<td>3000</td>\n<td>3500</td>\n<td>3500</td>\n<td>4000</td>\n<td>4500</td>\n</tr>\n<tr>\n<td>Working height(mm)</td>\n<td>4000</td>\n<td>5000</td>\n<td>5500</td>\n<td>5500</td>\n<td>6000</td>\n<td>6500</td>\n</tr>\n<tr>\n<td>Load capacity(kg)</td>\n<td>300</td>\n<td>300</td>\n<td>300</td>\n<td>300</td>\n<td>300</td>\n<td>300</td>\n</tr>\n<tr>\n<td>Platform size(mm)</td>\n<td>950\u00d7640</td>\n<td>950\u00d7640</td>\n<td>950\u00d7640</td>\n<td>950\u00d7640</td>\n<td>950\u00d7640</td>\n<td>950\u00d7640</td>\n</tr>\n<tr>\n<td>Batteries(V/Ah)</td>\n<td>2-12/120</td>\n<td>2-12/120</td>\n<td>2-12/120</td>\n<td>2-12/120</td>\n<td>2-12/120</td>\n<td>2-12/120</td>\n</tr>\n<tr>\n<td>Integrated charger(V/A)</td>\n<td>24/15</td>\n<td>24/15</td>\n<td>24/15</td>\n<td>24/15</td>\n<td>24/15</td>\n<td>24/15</td>\n</tr>\n<tr>\n<td>Drive motors(V/KW)</td>\n<td>2-24/0.5</td>\n<td>2-24/0.5</td>\n<td>2-24/0.5</td>\n<td>2-24/0.5</td>\n<td>2-24/0.5</td>\n<td>2-24/0.5</td>\n</tr>\n<tr>\n<td>Lifting motor(V/KW)</td>\n<td>DC 24/1.5</td>\n<td>DC 24/1.5</td>\n<td>DC 24/1.5</td>\n<td>DC 24/1.5</td>\n<td>DC 24/1.5</td>\n<td>DC 24/1.5</td>\n</tr>\n<tr>\n<td>Up/Down speed(mm/s)</td>\n<td>12/14</td>\n<td>20/22</td>\n<td>24/26</td>\n<td>17/19</td>\n<td>20/22</td>\n<td>23/25</td>\n</tr>\n<tr>\n<td>Maximum Drive Speeds-Stowed(Km/h)</td>\n<td>4</td>\n<td>4</td>\n<td>4</td>\n<td>4</td>\n<td>4</td>\n<td>4</td>\n</tr>\n<tr>\n<td>Maximum Drive Speeds-Raised(Km/h)</td>\n<td>1.1</td>\n<td>1.1</td>\n<td>1.1</td>\n<td>1.1</td>\n<td>1.1</td>\n<td>1.1</td>\n</tr>\n<tr>\n<td>Self-weight(kg)</td>\n<td>400</td>\n<td>574</td>\n<td>588</td>\n<td>655</td>\n<td>665</td>\n<td>675</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img11.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img11.png 367w, https://www.kijeka.com/wp-content/uploads/2017/11/img11-227x300.png 227w, https://www.kijeka.com/wp-content/uploads/2017/11/img11-270x356.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/semi-electric-order-picker-trucks/",
                "name": "Semi-Electric Order Picker Trucks",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Mobile order picker is an ergonocally designed for material picking and movement.</li>\n<li>Light design allows it to be easily transported by a single person.</li>\n<li>The light weight and manoeuvrability makes it convenient use in supermarket and warehouse.</li>\n<li>This semi electric order picker is electrically lift and manually pushed, it has been introduced as a lighter version of battery/electric operated lifting platform with the features that the operator will stand over the rising platform under full protection of railings</li>\n<li>The platform can accommodate one person with small packages, tools etc.</li>\n</ul>\n<p>\u00a0<br/>\n<strong>Features of Semi Electric Order Picker:</strong></p>\n<ul>\n<li>Emergency Down Button</li>\n<li>Emergency Stop Button</li>\n<li>Battery charge indicator</li>\n<li>Dual Brake</li>\n<li>Voltage indicator</li>\n<li>Safety brackets</li>\n<li>over loading limited</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td width=\"150\"><strong>Model</strong></td>\n<td colspan=\"5\" width=\"348\"><strong>Semi-Electric Order Picker Trucks</strong></td>\n</tr>\n<tr>\n<td width=\"150\">Platform height(mm)</td>\n<td width=\"72\">2720</td>\n<td width=\"66\">3300</td>\n<td width=\"66\">3500</td>\n<td width=\"72\">4000</td>\n<td width=\"72\">4500</td>\n</tr>\n<tr>\n<td width=\"150\">Working height(mm)</td>\n<td width=\"72\">4420</td>\n<td width=\"66\">5000</td>\n<td width=\"66\">5200</td>\n<td width=\"72\">5700</td>\n<td width=\"72\">6500</td>\n</tr>\n<tr>\n<td width=\"150\">Ground clearance(mm)</td>\n<td width=\"72\">30</td>\n<td width=\"66\">30</td>\n<td width=\"66\">30</td>\n<td width=\"72\">30</td>\n<td width=\"72\">30</td>\n</tr>\n<tr>\n<td width=\"150\">Load capacity(kg)</td>\n<td width=\"72\">200</td>\n<td width=\"66\">200</td>\n<td width=\"66\">200</td>\n<td width=\"72\">200</td>\n<td width=\"72\">200</td>\n</tr>\n<tr>\n<td width=\"150\">Platform size(mm)</td>\n<td width=\"72\">950\u00d7640</td>\n<td width=\"66\">950\u00d7640</td>\n<td width=\"66\">950\u00d7640</td>\n<td width=\"72\">950\u00d7640</td>\n<td width=\"72\">950\u00d7640</td>\n</tr>\n<tr>\n<td width=\"150\">Lift motor(V/Ah)</td>\n<td width=\"72\">12/1.6</td>\n<td width=\"66\">12/1.6</td>\n<td width=\"66\">12/1.6</td>\n<td width=\"72\">12/1.6</td>\n<td width=\"72\">12/1.6</td>\n</tr>\n<tr>\n<td width=\"150\">Batteries(V/Ah)</td>\n<td width=\"72\">12/120</td>\n<td width=\"66\">12/120</td>\n<td width=\"66\">12/120</td>\n<td width=\"72\">12/120</td>\n<td width=\"72\">12/120</td>\n</tr>\n<tr>\n<td width=\"150\">Integrated charger(V/A)</td>\n<td width=\"72\">12/15</td>\n<td width=\"66\">12/15</td>\n<td width=\"66\">12/15</td>\n<td width=\"72\">12/15</td>\n<td width=\"72\">12/15</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img10.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img10.png 321w, https://www.kijeka.com/wp-content/uploads/2017/11/img10-190x300.png 190w, https://www.kijeka.com/wp-content/uploads/2017/11/img10-270x426.png 270w"
                    ]
                ]
            }
        ],
        "Oil Pumps, Meters & Acces.": [
            {
                "link": "https://www.kijeka.com/product/product-air-operated-oil-ratio-drum-pump/",
                "name": "Air Operated Oil Ratio Drum Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Industrial Air Operated Oil Dispensing with best performance &amp; hassle free operation.</li>\n<li>These pumps are ideal for use in industry, workshop, farm, construction site or as part of Mobile oil System.</li>\n<li>All Metal, fully CNC Machined with hardened wear resistant moving parts.</li>\n</ul>\n<p>\u00a0</p>\n<table style=\"height: 484px;\" width=\"839\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"195\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td colspan=\"3\" width=\"399\"><strong>Air Operated Oil Ratio Drum Pump.</strong></td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"195\">Drive Type</td>\n<td width=\"135\"><strong>Air Operate </strong></td>\n<td width=\"122\"><strong>Air Operate </strong></td>\n<td width=\"142\"><strong>Air Operate </strong></td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"195\">Variants</td>\n<td width=\"135\"><strong>1:1\u00a0 Pump</strong></td>\n<td width=\"122\"><strong>3:1\u00a0 Pump</strong></td>\n<td width=\"142\"><strong>5:1 Pump</strong></td>\n</tr>\n<tr>\n<td width=\"156\">Pump MOC</td>\n<td width=\"39\"></td>\n<td width=\"135\">Steel, Brass,\n<p>Aluminium, Hi-Nitrile Rubber, Polyurethane</p>\n<p>Nylon</p></td>\n<td width=\"122\">Steel, Brass, Aluminium, Hi-Nitrile Rubber, Polyurethane,<br/>\nTurcite</td>\n<td width=\"142\">Steel, Brass, Aluminium, Hi-Nitrile Rubber, Polyurethane,<br/>\nTurcite</td>\n</tr>\n<tr>\n<td width=\"156\">Working Pressure</td>\n<td width=\"39\">\u00a0 Bar</td>\n<td width=\"135\">2-10 BAR</td>\n<td width=\"122\">2-10 BAR</td>\n<td width=\"142\">2-10 BAR</td>\n</tr>\n<tr>\n<td width=\"156\">Air Consumption</td>\n<td width=\"39\"></td>\n<td width=\"135\">270 LPM</td>\n<td width=\"122\">230 LPM</td>\n<td width=\"142\">250 LPM</td>\n</tr>\n<tr>\n<td width=\"156\">Air Inlet Connection</td>\n<td width=\"39\"></td>\n<td width=\"135\">1/4\u2033 BSP (F)</td>\n<td width=\"122\">1/4\u2033 BSP (F)</td>\n<td width=\"142\">1/4\u2033 BSP (F)</td>\n</tr>\n<tr>\n<td width=\"156\">Pump Outlet Connection</td>\n<td width=\"39\"></td>\n<td width=\"135\">1/2\u2033 BSP (F)</td>\n<td width=\"122\">1/2\u2033 BSP (F)</td>\n<td width=\"142\">1/2\u2033 BSP (F)</td>\n</tr>\n<tr>\n<td width=\"156\">Delivers</td>\n<td width=\"39\">LPM</td>\n<td width=\"135\">Up to 40 LPM</td>\n<td width=\"122\">Up to 14 LPM</td>\n<td width=\"142\">Up to 18 LPM</td>\n</tr>\n<tr>\n<td width=\"156\">Oil viscosity Range</td>\n<td width=\"39\"></td>\n<td width=\"135\">Up to SAE 80</td>\n<td width=\"122\">Up to SAE 130</td>\n<td width=\"142\">Up to SAE 240</td>\n</tr>\n<tr>\n<td width=\"156\">Noise Level</td>\n<td width=\"39\">db</td>\n<td width=\"135\">81 db</td>\n<td width=\"122\">81 db</td>\n<td width=\"142\">81 db</td>\n</tr>\n<tr>\n<td width=\"156\">For Use with</td>\n<td width=\"39\"></td>\n<td width=\"135\">210 litre Drums</td>\n<td width=\"122\">210 litre Drums</td>\n<td width=\"142\">210 litre Drums</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Air-Operated-Oil-Ratio-Pump.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Air-Operated-Oil-Ratio-Pump.jpg 206w, https://www.kijeka.com/wp-content/uploads/2017/06/Air-Operated-Oil-Ratio-Pump-62x300.jpg 62w, https://www.kijeka.com/wp-content/uploads/2017/06/Air-Operated-Oil-Ratio-Pump-72x350.jpg 72w, https://www.kijeka.com/wp-content/uploads/2017/06/Air-Operated-Oil-Ratio-Pump-99x480.jpg 99w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/electric-oil-transfer-pump-2/",
                "name": "Electric Oil Transfer Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Self-priming, positive displacement design Pump.</li>\n<li>Heavy duty oil pump designed to transfer bulk oils, hydraulic oils, used oil etc.</li>\n<li>Aluminium Die cast, Air cooled motor with thermal protection.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"548\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"258\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"291\"><strong>Electric Oil Transfer Pump. </strong></td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Flow Rate</td>\n<td width=\"291\">Upto 25 LPM</td>\n</tr>\n<tr>\n<td width=\"210\">Drive Type</td>\n<td width=\"48\"></td>\n<td width=\"291\">Electric Operated</td>\n</tr>\n<tr>\n<td width=\"210\">Motor</td>\n<td width=\"48\">hp</td>\n<td width=\"291\">1/2 HP 220V AC</td>\n</tr>\n<tr>\n<td width=\"210\">RPM</td>\n<td width=\"48\">Bar</td>\n<td width=\"291\">2800/3360</td>\n</tr>\n<tr>\n<td width=\"210\">Mechanism</td>\n<td width=\"48\"></td>\n<td width=\"291\">Gear Pump</td>\n</tr>\n<tr>\n<td width=\"210\">Inlet</td>\n<td width=\"48\"></td>\n<td width=\"291\">1\u2033 NPT</td>\n</tr>\n<tr>\n<td width=\"210\">Outlet</td>\n<td width=\"48\"></td>\n<td width=\"291\">3/4\u2033 NPT</td>\n</tr>\n<tr>\n<td width=\"210\">Suction Pipe</td>\n<td width=\"48\">Inch</td>\n<td width=\"291\">34\u2033 long</td>\n</tr>\n<tr>\n<td width=\"210\">Discharge Hose</td>\n<td width=\"48\"></td>\n<td width=\"291\">3/4\u2033 x 8 Feet Long</td>\n</tr>\n<tr>\n<td width=\"210\">MAX. Viscosity Of Oil</td>\n<td width=\"48\"></td>\n<td width=\"291\">SAE 90</td>\n</tr>\n<tr>\n<td width=\"210\">MAX Working Pressure</td>\n<td width=\"48\">PSI</td>\n<td width=\"291\">65 PSI (4.5 BAR)</td>\n</tr>\n<tr>\n<td width=\"210\">Wetted Components</td>\n<td width=\"48\"></td>\n<td width=\"291\">Aluminium, Steel, Cast Iron, Nylon, NBR, Zinc, Polypropylene, PVC</td>\n</tr>\n<tr>\n<td width=\"210\">Recommended Use</td>\n<td width=\"48\"></td>\n<td width=\"291\">Oils, Synthetic Oils, Used Oils, Hydraulic Oils, Cutting Oils, Oil Based Herbicides, Non-Flammable Oil Based Solvents, Liquid Soap etc</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Oil-Transfer-pump.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Oil-Transfer-pump.jpg 668w, https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Oil-Transfer-pump-212x300.jpg 212w, https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Oil-Transfer-pump-64x90.jpg 64w, https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Oil-Transfer-pump-248x350.jpg 248w, https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Oil-Transfer-pump-340x480.jpg 340w, https://www.kijeka.com/wp-content/uploads/2017/06/Electric-Oil-Transfer-pump-270x382.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/lever-action-drum-pump/",
                "name": "Lever Action Drum Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Oil pump designed &amp; engineered for convenient use &amp; long service life</li>\n<li>Complete with curved metal spout &amp; telescopic suction tube for use on 50-210 litre drum.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"548\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"258\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"291\"><strong>Lever Action Drum Pump.</strong></td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Drive Type</td>\n<td width=\"291\">Manual/ Hand Operated</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Delivers</td>\n<td width=\"291\">300ml Per Stroke</td>\n</tr>\n<tr>\n<td width=\"210\">Wetted Components</td>\n<td width=\"48\"></td>\n<td width=\"291\">Steel, Aluminium, NBR, Brass, PVC</td>\n</tr>\n<tr>\n<td width=\"210\">Recommended Use</td>\n<td width=\"48\"></td>\n<td width=\"291\">Oil Based Fluids, Heating Oils, Motor Oil, Heavy &amp; Light Oils, Kerosene &amp; Diesel</td>\n</tr>\n<tr>\n<td width=\"210\">Do not Use with</td>\n<td width=\"48\"></td>\n<td width=\"291\">Water Based Fluids, Solvents, Acids, Petrol etc.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Lever-Action-Pump-scaled.jpg"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/oil-control-gun-with-electronic-meter/",
                "name": "Oil Control Gun with Electronic Meter",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Heavy duty oil control gun with robust aluminium construction</li>\n<li>Electronic preset design; works on 4 x 1.5V AA batteries</li>\n<li>Dual Mode: Manual &amp; Pre-Set (dispenses set quantity of media &amp; stops)</li>\n<li>Oval gear mechanism for optimum accuracy</li>\n<li>Lifetime non-resettable totalizer can be set in litres</li>\n<li>Built-in swivel at Inlet fitted with strainer</li>\n</ul>\n<p><u>\u00a0</u></p>\n<table width=\"548\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"258\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"291\"><strong>Oil Control Gun with Electronic\u00a0 Meter </strong></td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Flow Rate</td>\n<td width=\"291\">1-30 LPM</td>\n</tr>\n<tr>\n<td width=\"210\">Inlet</td>\n<td width=\"48\"></td>\n<td width=\"291\">1/2\u2033 BSP (F)</td>\n</tr>\n<tr>\n<td width=\"210\">Accuracy</td>\n<td width=\"48\"></td>\n<td width=\"291\">\u00b1 0.50%</td>\n</tr>\n<tr>\n<td width=\"210\">Repeat Ability</td>\n<td width=\"48\"></td>\n<td width=\"291\">\u00b1 0.20%</td>\n</tr>\n<tr>\n<td width=\"210\">Maximum Working Pressure</td>\n<td width=\"48\">PSI</td>\n<td width=\"291\">1,000 PSI (70 BAR)</td>\n</tr>\n<tr>\n<td width=\"210\">Temperature</td>\n<td width=\"48\"><sup>O</sup>C</td>\n<td width=\"291\">-5<sup>O </sup>C to 50 <sup>O</sup></td>\n</tr>\n<tr>\n<td width=\"210\">Minimum Pre Set Qty.</td>\n<td width=\"48\"></td>\n<td width=\"291\">0.10 units</td>\n</tr>\n<tr>\n<td width=\"210\">Maximum Pre Set Qty.</td>\n<td width=\"48\"></td>\n<td width=\"291\">99.9 units</td>\n</tr>\n<tr>\n<td width=\"210\">MAX. Resettable Batch Totalizer</td>\n<td width=\"48\"></td>\n<td width=\"291\">999.9</td>\n</tr>\n<tr>\n<td width=\"210\">MAX. Non Resettable Batch Totalizer</td>\n<td width=\"48\"></td>\n<td width=\"291\">999999 units</td>\n</tr>\n<tr>\n<td width=\"210\">Viscosity of Media Dispensed</td>\n<td width=\"48\"></td>\n<td width=\"291\">10 to 5000 cst</td>\n</tr>\n<tr>\n<td width=\"210\">Resolution/ Least Count</td>\n<td width=\"48\"></td>\n<td width=\"291\">0.0005 litre</td>\n</tr>\n<tr>\n<td width=\"210\">Water Resistance</td>\n<td width=\"48\"></td>\n<td width=\"291\">IP55</td>\n</tr>\n<tr>\n<td width=\"210\">Wetted Components</td>\n<td width=\"48\"></td>\n<td width=\"291\">Aluminium, Steel, Stainless Steel, Brass, Polyurethane, Acetic Resin, Hi Nitrile Rubber</td>\n</tr>\n<tr>\n<td width=\"210\">Recommended Use</td>\n<td width=\"48\"></td>\n<td width=\"291\">Oils with viscosity in the range of 10 to 5000 cst, Diesel</td>\n</tr>\n<tr>\n<td width=\"210\">Do Not Use With</td>\n<td width=\"48\"></td>\n<td width=\"291\">Petrol, Windshield Fluids etc.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Electronic-Meter.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Electronic-Meter.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Electronic-Meter-212x300.jpg 212w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Electronic-Meter-768x1086.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Electronic-Meter-724x1024.jpg 724w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Electronic-Meter-64x90.jpg 64w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Electronic-Meter-248x350.jpg 248w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Electronic-Meter-339x480.jpg 339w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Electronic-Meter-270x382.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/oil-control-gun-with-mechanical-meter/",
                "name": "Oil Control Gun with Mechanical Meter",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Super accuracy heavy duty gun for controlling fluid deliveries in most demanding applications</li>\n<li>Oval gear mechanism, High accuracy mechanical display</li>\n<li>Supplied complete with rigid steel extension, and manual non drip nozzle.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"548\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"258\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"291\"><strong>Oil Control Gun with Mechanical\u00a0 Meter </strong></td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Flow Rate</td>\n<td width=\"291\">1-30 LPM</td>\n</tr>\n<tr>\n<td width=\"210\">Inlet</td>\n<td width=\"48\"></td>\n<td width=\"291\">1/2\u2033 BSP (F)</td>\n</tr>\n<tr>\n<td width=\"210\">Accuracy</td>\n<td width=\"48\"></td>\n<td width=\"291\">\u00b1 1 %</td>\n</tr>\n<tr>\n<td width=\"210\">Repeat Ability</td>\n<td width=\"48\"></td>\n<td width=\"291\">\u00b1 0.30%</td>\n</tr>\n<tr>\n<td width=\"210\">Maximum Working Pressure</td>\n<td width=\"48\">PSI</td>\n<td width=\"291\">1,000 PSI (70 BAR)</td>\n</tr>\n<tr>\n<td width=\"210\">Temperature</td>\n<td width=\"48\"><sup>O</sup>C</td>\n<td width=\"291\">-5<sup>O </sup>C to 50 <sup>O</sup></td>\n</tr>\n<tr>\n<td width=\"210\">MAX. Resettable Batch Totalizer</td>\n<td width=\"48\"></td>\n<td width=\"291\">999.9</td>\n</tr>\n<tr>\n<td width=\"210\">MAX. Non Resettable Batch Totalizer</td>\n<td width=\"48\"></td>\n<td width=\"291\">999999.9 units</td>\n</tr>\n<tr>\n<td width=\"210\">Resolution/ Least Count</td>\n<td width=\"48\"></td>\n<td width=\"291\">0.10 litre</td>\n</tr>\n<tr>\n<td width=\"210\">Water Resistance</td>\n<td width=\"48\"></td>\n<td width=\"291\">IP55</td>\n</tr>\n<tr>\n<td width=\"210\">Wetted Components</td>\n<td width=\"48\"></td>\n<td width=\"291\">Aluminium, Acetal, Nitrile Rubber &amp; Steel</td>\n</tr>\n<tr>\n<td width=\"210\">Recommended Use</td>\n<td width=\"48\"></td>\n<td width=\"291\">Oils Upto SAE 140, Diesel, Kerosene &amp; Engine Coolants (RTU)</td>\n</tr>\n<tr>\n<td width=\"210\">Do Not Use With</td>\n<td width=\"48\"></td>\n<td width=\"291\">Water Based Media, Petrol etc.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Mechenical-Meter-copy.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Mechenical-Meter-copy.jpg 956w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Mechenical-Meter-copy-138x300.jpg 138w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Mechenical-Meter-copy-768x1674.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Mechenical-Meter-copy-470x1024.jpg 470w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Mechenical-Meter-copy-41x90.jpg 41w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Mechenical-Meter-copy-161x350.jpg 161w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Mechenical-Meter-copy-220x480.jpg 220w, https://www.kijeka.com/wp-content/uploads/2017/06/Oil-Control-Gun-with-Mechenical-Meter-copy-270x589.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/plastic-funnels/",
                "name": "Plastic Funnels",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Heavy duty translucent polypropylene construction.</li>\n<li>Anti-splash &amp; spill proof, with rim of the funnel curved in.</li>\n<li>Complete with wire mesh screen, dust cover &amp; flexible spout.</li>\n<li>Available in 2 sizes. The larger size is available with drum bung attachment, which allows the funnel to be mounted direct onto drums with 2\u2033 threaded opening.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"548\">\n<tbody>\n<tr>\n<td width=\"258\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"291\"><strong>Plastic Funnels.</strong></td>\n</tr>\n<tr>\n<td width=\"258\">Available Capacity</td>\n<td width=\"291\">1.7 Litres &amp; 3 Litres</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Plastic-Funnels.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/rotary-action-drum-pump/",
                "name": "Rotary Action Drum Pump",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Most popularly used pump for general purpose lubrication on farms, automotive, workshops &amp; construction sites</li>\n<li>Pump features a dual directional operation that allows the pump to both empty as well as refill container</li>\n<li>Rugged cast iron construction with machined vanes for better draw &amp; smoother delivery.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"548\">\n<tbody>\n<tr>\n<td colspan=\"2\" width=\"258\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"291\"><strong>Rotary Action Drum Pump. </strong><strong>KE 202</strong></td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Drive Type</td>\n<td width=\"291\">Manual/ Hand Operated</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"258\">Delivers</td>\n<td width=\"291\">5 litres Per 20 Turns</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"210\">Wetted Components</td>\n<td width=\"291\">Steel, Cast Iron, NBR</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"210\">Recommended Use</td>\n<td width=\"291\">Heating Oils, Motor Oils, Lubricating Oils etc.</td>\n</tr>\n<tr>\n<td colspan=\"2\" width=\"210\">Do not Use with</td>\n<td width=\"291\">Water based Media, Acids, Petrol etc.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Action-Drum-Pump.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Action-Drum-Pump.jpg 945w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Action-Drum-Pump-212x300.jpg 212w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Action-Drum-Pump-768x1087.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Action-Drum-Pump-724x1024.jpg 724w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Action-Drum-Pump-64x90.jpg 64w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Action-Drum-Pump-247x350.jpg 247w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Action-Drum-Pump-339x480.jpg 339w, https://www.kijeka.com/wp-content/uploads/2017/06/Rotary-Action-Drum-Pump-270x382.jpg 270w"
                    ]
                ]
            }
        ],
        "Pallet Trucks": [
            {
                "link": "https://www.kijeka.com/product/rough-terrain-pallet-truck/",
                "name": "All-Terrain Pallet Truck",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>The manual rough terrain pallet truck has been designed to travel over irregular areas where ordinary pallet trucks have difficulty</strong>.</li>\n<li>It is ideally suited for nurseries, builders yards and construction sites.</li>\n<li><strong>Capacity: \u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 1000 kgs.</strong></li>\n<li>Fork Length:\u00a0 \u00a0 \u00a0\u00a0 \u00a0 \u00a0 \u00a0 \u00a01200 mm</li>\n<li>Fork Width :\u00a0 \u00a0 \u00a0 \u00a0 \u00a0 \u00a0 \u00a0 \u00a0 150 mm</li>\n<li>Adjustable width between forks</li>\n<li>Fork Height:\u00a0 \u00a0 \u00a0 \u00a0 \u00a0 \u00a0 \u00a0 \u00a0 90 mm</li>\n<li>Erected Fork Height:\u00a0 \u00a0200mm</li>\n<li>Reliable oil leak-proof hydraulic system.</li>\n<li>Solid Rubber Wheels with double ball bearing requires less pulling efforts at full capacity.</li>\n<li>Best Quality in India</li>\n</ul>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/All-Terrain-Rough-Pallet-Truck.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/All-Terrain-Rough-Pallet-Truck.jpg 851w, https://www.kijeka.com/wp-content/uploads/2021/04/All-Terrain-Rough-Pallet-Truck-280x300.jpg 280w, https://www.kijeka.com/wp-content/uploads/2021/04/All-Terrain-Rough-Pallet-Truck-768x822.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/All-Terrain-Rough-Pallet-Truck-70x75.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/All-Terrain-Rough-Pallet-Truck-270x289.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/All-Terrain-Rough-Pallet-Truck-370x396.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/customized-pallet-truck/",
                "name": "Customized Pallet Truck",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>We also design specialty pallet jacks for your unique application</strong></li>\n<li>For most needs, we offer a wide range of pallet jack profiles and capacities, but we can meet almost any need for custom orders</li>\n<li><strong>Customize Narrow forks, short forks, long forks, low profile forks, special wheels and rollers</strong></li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Customized Pallet Trucks\u00a0 </strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Capacity</td>\n<td width=\"324\">2500 kgs, 3500 Kgs, 5000 kgs</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Fork Length</strong></td>\n<td width=\"324\"><strong>As Per Custom Requirement</strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Overall Fork Width</strong></td>\n<td width=\"324\"><strong>As Per Custom Requirement</strong></td>\n</tr>\n<tr>\n<td width=\"198\">Size Of Fork</td>\n<td width=\"324\">150 x 65mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lower Fork Height</td>\n<td width=\"324\">90-100mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lifting Height</td>\n<td width=\"324\">200mm</td>\n</tr>\n<tr>\n<td width=\"198\">Steering Wheels Size/ MOC</td>\n<td width=\"324\">180mm x 50mm \u2013 MS/Nylon/PU/ UHMW</td>\n</tr>\n<tr>\n<td width=\"198\">Load Roller Size/ MOC</td>\n<td width=\"324\">82mm x 70mm- \u00a0MS/Nylon/PU/ UHMW</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Customized-Pallet-Truck.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Customized-Pallet-Truck.png 484w, https://www.kijeka.com/wp-content/uploads/2017/11/Customized-Pallet-Truck-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/11/Customized-Pallet-Truck-300x300.png 300w, https://www.kijeka.com/wp-content/uploads/2017/11/Customized-Pallet-Truck-270x270.png 270w, https://www.kijeka.com/wp-content/uploads/2017/11/Customized-Pallet-Truck-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/electric-high-lift-pallet-truck/",
                "name": "Electric High Lift Pallet Truck",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>This 800mm high lift pallet truck is part of our wide range of high lift pallet truck</li>\n<li>High Lift Pallet Truck piece reduces the physical effort needed by staff members and considerably improves the ergonomic conditions at work stations by raising the trucks to the desired height. Preventing bending and stooping, it can employees to remain safe and avoid back problems \u2013 a major cause of sick days within the UK.</li>\n<li><strong>Electric operated pump unit.</strong></li>\n<li>Auto locking prevents the unit from moving when the forks are raised to ensure the safety of the operator.</li>\n<li>Truck automatically slows the descending speed when heavy goods are loaded to help prevent cargo damage.</li>\n<li>This pallet truck is not suitable for closed bottom pallets or any load which is off center or overhangs the pallet footprint and may cause the unit to be out of balance.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Electric High Lift Pallet Trucks \u00a0\u00a0</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Electric \u00a0Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Capacity</td>\n<td width=\"324\">1000 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Length</td>\n<td width=\"324\">1150mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lower Fork Height</td>\n<td width=\"324\">90-100mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lifting Height</td>\n<td width=\"324\">800mm</td>\n</tr>\n<tr>\n<td width=\"198\">Steering Wheels Size/MOC</td>\n<td width=\"324\">180mm x 50mm/ Nylon- Polyurethane</td>\n</tr>\n<tr>\n<td width=\"198\">Load Roller Size/MOC</td>\n<td width=\"324\">82mm x 70mm/ Nylon- Polyurethane</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Electric-High-Lift-Pallet-Truck.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Electric-High-Lift-Pallet-Truck.png 484w, https://www.kijeka.com/wp-content/uploads/2017/11/Electric-High-Lift-Pallet-Truck-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/11/Electric-High-Lift-Pallet-Truck-300x300.png 300w, https://www.kijeka.com/wp-content/uploads/2017/11/Electric-High-Lift-Pallet-Truck-270x270.png 270w, https://www.kijeka.com/wp-content/uploads/2017/11/Electric-High-Lift-Pallet-Truck-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/heavy-duty-pallet-truck-5000kgs/",
                "name": "Heavy Duty Pallet Truck (5000Kgs)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Heavy Duty Pallet truck with Full hydraulic system. Bullet connection between steering shaft and pump piston. It is convenient to replace the rear wheel.</li>\n<li>Easy to maneuver with 210 degrees turning radius. Special lowering valve to control the trucks durable. Number of pump strokes-10. Lift height per stroke: 12MM</li>\n<li>Reliable oil leak-proof hydraulic system with Lubrication grease nipples on all movable parts for easy maintenance.</li>\n<li>Finger Tip Lever\u00a0Control Handle\u00a0for selecting, raising, Neutral Or Lowering Position. Handle Automatically Return to vertical Position Ergonomic Large Rubber handle with three control lever.</li>\n<li>Nylon Wheels with sealed precision bearing requires less\u00a0pulling efforts At full capacity.</li>\n<li>Nylon ROLLER 80mm DIA. For easy entry &amp; exit with nose Tip Roller.</li>\n<li>Ideal Handling on uneven floor &amp; Lower ground Pressure</li>\n</ul>\n<table>\n<tbody>\n<tr>\n<td><strong>Model</strong></td>\n<td><strong>Hydraulic Hand Pallet Trucks\u00a0 </strong></td>\n</tr>\n<tr>\n<td>MOC</td>\n<td>MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td>Drive Type</td>\n<td>Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td><strong>Capacity</strong></td>\n<td><strong>5000 kgs</strong></td>\n</tr>\n<tr>\n<td><strong>Fork Length</strong></td>\n<td><strong>1150mm / 1220mm</strong></td>\n</tr>\n<tr>\n<td><strong>Overall Fork Width</strong></td>\n<td><strong>550mm / 685 mm</strong></td>\n</tr>\n<tr>\n<td>Size Of Fork</td>\n<td>150 x 65mm</td>\n</tr>\n<tr>\n<td>Lower Fork Height</td>\n<td>90-100mm</td>\n</tr>\n<tr>\n<td><strong>Lifting Height</strong></td>\n<td><strong>200mm</strong></td>\n</tr>\n<tr>\n<td>Steering Wheels Size/MOC</td>\n<td>180mm x 50mm/ Nylon- Polyurethane</td>\n</tr>\n<tr>\n<td>Load Roller Size/MOC</td>\n<td>82mm x 70mm/ Nylon- Polyurethane</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-3-scaled-e1618286925905.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-3-scaled-e1618286925905.jpg 2041w, https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-3-scaled-e1618286925905-300x240.jpg 300w, https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-3-scaled-e1618286925905-1024x819.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-3-scaled-e1618286925905-768x614.jpg 768w, https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-3-scaled-e1618286925905-1536x1228.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-3-scaled-e1618286925905-70x56.jpg 70w, https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-3-scaled-e1618286925905-270x216.jpg 270w, https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-3-scaled-e1618286925905-370x296.jpg 370w, https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-3-scaled-e1618286925905-1170x936.jpg 1170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-1-scaled-e1618287139710-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-1-scaled-e1618287139710-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-1-scaled-e1618287139710-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-2-scaled-e1618287026118-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-2-scaled-e1618287026118-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2021/04/Pallet-Truck.-KE303-NY-5T-1150L-550W-2-scaled-e1618287026118-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/product-high-lift-pallet-truck/",
                "name": "High Lift Pallet Truck",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Scissor lift truck can be used for transportation or work platform</li>\n<li>High Lift Pallet Truck body design is compact, fast lifting pump function, saving time and improve labor efficiency; widely used in factories, workshops, warehouses, supermarkets, etc. Location.</li>\n<li><strong>Lifting range can be adapted to different handling height, reducing the bending troubles handling goods</strong></li>\n<li><strong>Combination of pallet truck and lifting platform functions</strong></li>\n<li>Advanced hydraulic system with rapid promotion, high efficiency;</li>\n<li>High quality, reliable, long life, good sealing effect.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>High Lift Pallet Trucks \u00a0\u00a0</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Capacity</td>\n<td width=\"324\">800 kgs / 1000 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Length</td>\n<td width=\"324\">1150mm / 1220mm</td>\n</tr>\n<tr>\n<td width=\"198\">Overall Fork Width</td>\n<td width=\"324\">550mm / 685 mm</td>\n</tr>\n<tr>\n<td width=\"198\">Size Of Fork</td>\n<td width=\"324\">150 x 65mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lower Fork Height</td>\n<td width=\"324\">90-100mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lifting Height</td>\n<td width=\"324\">800mm / 1000mm</td>\n</tr>\n<tr>\n<td width=\"198\">Steering Wheels Size/MOC</td>\n<td width=\"324\">180mm x 50mm/ Nylon- Polyurethane</td>\n</tr>\n<tr>\n<td width=\"198\">Load Roller Size/MOC</td>\n<td width=\"324\">82mm x 70mm/ Nylon- Polyurethane</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/High-Lift-Pallet-Truck-1.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/High-Lift-Pallet-Truck-1.png 443w, https://www.kijeka.com/wp-content/uploads/2017/11/High-Lift-Pallet-Truck-1-275x300.png 275w, https://www.kijeka.com/wp-content/uploads/2017/11/High-Lift-Pallet-Truck-1-270x295.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/hybrid-pallet-truck/",
                "name": "Hybrid Pallet Truck",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>All New Hybrid Pallet Truck is a 1.5 ton capacity pallet truck, powered by 20Ah portable Lithium battery.</li>\n<li>It takes just 2 hours to fully charge the battery; what\u2019s more, the battery is designed for easier access and replacement within 20 seconds.</li>\n<li>Due to this creative structure and quick changing of battery working efficiency is greatly enhanced.</li>\n<li>Main components of Hybrid Pallet Truck feature a modular design, making operation much easier, and doing away with the service cover.</li>\n<li>Even if the truck is out of power during its working cycle, the Hybrid can be used as manual pallet truck.</li>\n<li>It is a simple and smarter body structure, operationally friendly, and requires minimum maintenance.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"228\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"294\"><strong>Hybrid Pallet Trucks\u00a0 </strong></td>\n</tr>\n<tr>\n<td width=\"228\">MOC</td>\n<td width=\"294\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"228\">Operation \u00a0Type</td>\n<td width=\"294\">Walkie</td>\n</tr>\n<tr>\n<td width=\"228\">Standard Capacity</td>\n<td width=\"294\">1500 kgs</td>\n</tr>\n<tr>\n<td width=\"228\">Load Center</td>\n<td width=\"294\">600mm</td>\n</tr>\n<tr>\n<td width=\"228\">Fork Length</td>\n<td width=\"294\">1150mm</td>\n</tr>\n<tr>\n<td width=\"228\">Overall Fork Width</td>\n<td width=\"294\">550mm</td>\n</tr>\n<tr>\n<td width=\"228\">Size Of Fork</td>\n<td width=\"294\">150 x 65mm</td>\n</tr>\n<tr>\n<td width=\"228\">Lower Fork Height</td>\n<td width=\"294\">85mm</td>\n</tr>\n<tr>\n<td width=\"228\">Lifting Height</td>\n<td width=\"294\">200mm</td>\n</tr>\n<tr>\n<td width=\"228\"><strong>Travel Speed (laden/unladen)</strong></td>\n<td width=\"294\"><strong>4/4.5kmh</strong></td>\n</tr>\n<tr>\n<td width=\"228\"><strong>Battery Voltage/ Capacity</strong></td>\n<td width=\"294\"><strong>24V/20Ah Li-Battery</strong></td>\n</tr>\n<tr>\n<td width=\"228\">Turning Radius</td>\n<td width=\"294\">1320mm/1390mm</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Hybrid-Pallet-Truck.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Hybrid-Pallet-Truck.png 342w, https://www.kijeka.com/wp-content/uploads/2017/11/Hybrid-Pallet-Truck-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/11/Hybrid-Pallet-Truck-300x300.png 300w, https://www.kijeka.com/wp-content/uploads/2017/11/Hybrid-Pallet-Truck-270x270.png 270w, https://www.kijeka.com/wp-content/uploads/2017/11/Hybrid-Pallet-Truck-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/hydraulic-hand-pallet-trucks/",
                "name": "Hydraulic Hand Pallet Truck",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>A\u00a0pallet Trucks, also known as a\u00a0pallet Jackpallet pump,\u00a0Pump truck</li>\n<li>Pallet Truck is a tool used to lift and move\u00a0pallets.</li>\n<li>Pallet jacks are the most basic form of a\u00a0forklift and are intended to move heavy or light Pallets within a warehouse.</li>\n<li>Hydraulic Hand Pallet Truck that has high load bearing capacity and is provided with Polyurethane / UHMW-PE tandem rollers for quieter and smoother rolling over rough surfaces.</li>\n<li>It is also equipped with a one-piece \u201cC\u201d section forks for greater strength and a sully strengthened chassis along inside of forks.</li>\n</ul>\n<ul>\n<li>Available options: Manual, Weight Scale, Battery operator.</li>\n<li>Choice: Special fork length, width, wheels &amp; capacity as per requirement.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Hydraulic Hand Pallet Trucks\u00a0 </strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Capacity</td>\n<td width=\"324\">2500 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Length</td>\n<td width=\"324\">1150mm / 1220mm</td>\n</tr>\n<tr>\n<td width=\"198\">Overall Fork Width</td>\n<td width=\"324\">550mm / 685 mm</td>\n</tr>\n<tr>\n<td width=\"198\">Size Of Fork</td>\n<td width=\"324\">150 x 65mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lower Fork Height</td>\n<td width=\"324\">90-100mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lifting Height</td>\n<td width=\"324\">200mm</td>\n</tr>\n<tr>\n<td width=\"198\">Steering Wheels Size/MOC</td>\n<td width=\"324\">180mm x 50mm/ Nylon- Polyurethane</td>\n</tr>\n<tr>\n<td width=\"198\">Load Roller Size/MOC</td>\n<td width=\"324\">82mm x 70mm/ Nylon- Polyurethane</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Available Capacity</strong></td>\n<td width=\"324\"><strong>2500 Kgs , 3000 Kgs, 5000 Kgs.</strong></td>\n</tr>\n<tr>\n<td width=\"198\">Other Drive Option</td>\n<td width=\"324\">Battery Operated</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Other Option </strong></td>\n<td width=\"324\"><strong>Special fork length, width, wheels &amp; capacity </strong>\n<p><strong>As per Client Requirement.</strong></p></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Pallet-Trucks.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Pallet-Trucks.png 299w, https://www.kijeka.com/wp-content/uploads/2017/11/Pallet-Trucks-279x300.png 279w, https://www.kijeka.com/wp-content/uploads/2017/11/Pallet-Trucks-270x290.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/mini-battery-operated-pallet-truck/",
                "name": "Mini Battery Operated Pallet Truck",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>This type of Semi Electric Pallet Truck has been use for easy transportation of pallets in big plants &amp; warehouses. For a long travel in plants it is a versatile machine to handle the pallets safely &amp; quickly with minimum efforts, with lifting lowering manually Hydraulic to cut the cost and Traveling Battery Drive.</li>\n<li>Heavy duty design, Best value with many applications.</li>\n<li>Powered travel with compact and robust structure.</li>\n<li>Low maintenance, low weight and low profile for good operating visibility.</li>\n<li>High quality electric components and drive wheel.</li>\n<li>Drive Wheel: Complete gear train mounted on ball and roller bearing in oil bath housing.</li>\n<li>High-torque horizontally mounted motor has copper graphite brushes for excellent Lubrication.</li>\n<li>To avoid any accident maximum safety features are provided as push stop, horn &amp; automatic brakes in handle, with forward &amp; reverse movement system.</li>\n<li>Operator can control easily the whole systems for lifting, Lowering &amp; transportation of loaded pallets.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td width=\"174\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"333\"><strong>Mini Battery Operated Pallet Truck</strong></td>\n</tr>\n<tr>\n<td width=\"174\">Drive Unit</td>\n<td width=\"333\">Battery</td>\n</tr>\n<tr>\n<td width=\"174\">Operator Type</td>\n<td width=\"333\"><em>Walkie\u00a0</em></td>\n</tr>\n<tr>\n<td width=\"174\"><strong>Load Capacity</strong></td>\n<td width=\"333\"><strong>1500</strong></td>\n</tr>\n<tr>\n<td width=\"174\">Load Center</td>\n<td width=\"333\">600</td>\n</tr>\n<tr>\n<td width=\"174\">Load Distance (Raised)</td>\n<td width=\"333\">883/946</td>\n</tr>\n<tr>\n<td width=\"174\">Wheelbase</td>\n<td width=\"333\">1250</td>\n</tr>\n<tr>\n<td width=\"174\">Tyre Type</td>\n<td width=\"333\">PU</td>\n</tr>\n<tr>\n<td width=\"174\">Tyre size, operator side</td>\n<td width=\"333\">210 x 70</td>\n</tr>\n<tr>\n<td width=\"174\">Tyre size, load side</td>\n<td width=\"333\">80 x 60</td>\n</tr>\n<tr>\n<td width=\"174\">Lift Height</td>\n<td width=\"333\">115</td>\n</tr>\n<tr>\n<td width=\"174\">Fork height, lowered</td>\n<td width=\"333\">90</td>\n</tr>\n<tr>\n<td width=\"174\">Battery Type</td>\n<td width=\"333\">Maintenance free battery</td>\n</tr>\n<tr>\n<td width=\"174\">Type of drive control</td>\n<td width=\"333\">DC</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Mini-Battery-Operated-Pallet-Truck.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/pallet-truck-with-cargo-backrest-2/",
                "name": "Pallet Truck-with Cargo Backrest",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Pallet Jack Trucks with Cargo Backrest allow stacked boxes and taller loads to be moved safely and easily. </strong></li>\n<li>Steel Backrest is factory installed on the Truck. Industrial grade hydraulic pump smoothly raises and lowers skids or pallets and includes a safety overload bypass valve.</li>\n<li>Pallet Jacks feature a 3-function hand control (Raise, Neutral and Lower) and offer a spring-loaded self-righting safety loop handle to enhance comfort and ease of operation.</li>\n<li>Wide tapered forks include entry and exit rollers for smooth operation.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Pallet Trucks- With Cargo Backrest\u00a0 </strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Capacity</td>\n<td width=\"324\">2500 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Length</td>\n<td width=\"324\">1150mm / 1220mm</td>\n</tr>\n<tr>\n<td width=\"198\">Overall Fork Width</td>\n<td width=\"324\">550mm / 685 mm</td>\n</tr>\n<tr>\n<td width=\"198\">Size Of Fork</td>\n<td width=\"324\">150 x 65mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lower Fork Height</td>\n<td width=\"324\">90-100mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lifting Height</td>\n<td width=\"324\">200mm</td>\n</tr>\n<tr>\n<td width=\"198\">Steering Wheels Size/MOC</td>\n<td width=\"324\">180mm x 50mm/ Nylon- Polyurethane</td>\n</tr>\n<tr>\n<td width=\"198\">Load Roller Size/MOC</td>\n<td width=\"324\">82mm x 70mm/ Nylon- Polyurethane</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Backrest Height </strong></td>\n<td width=\"324\"><strong>50 Inch </strong></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Pallet-Truck-with-Cargo-Backrest-1.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Pallet-Truck-with-Cargo-Backrest-1.png 369w, https://www.kijeka.com/wp-content/uploads/2017/11/Pallet-Truck-with-Cargo-Backrest-1-300x274.png 300w, https://www.kijeka.com/wp-content/uploads/2017/11/Pallet-Truck-with-Cargo-Backrest-1-270x247.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/pallet-trucks-spares/",
                "name": "Pallet Trucks Spares",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>We offer all Type of Pallet Truck Spare Part, Pallet Truck Wheel-Nylon/PU, Pin, Pallet Pump for Replacement, Seal Kit, Repairing of any Brand Hydraulic Cylinders</strong></li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Pallet-Truck-Spares.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/12/Pallet-Truck-Spares.jpg 2494w, https://www.kijeka.com/wp-content/uploads/2017/12/Pallet-Truck-Spares-300x144.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/12/Pallet-Truck-Spares-1024x491.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2017/12/Pallet-Truck-Spares-768x368.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/12/Pallet-Truck-Spares-1536x737.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2017/12/Pallet-Truck-Spares-2048x982.jpg 2048w, https://www.kijeka.com/wp-content/uploads/2017/12/Pallet-Truck-Spares-70x34.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/12/Pallet-Truck-Spares-370x177.jpg 370w, https://www.kijeka.com/wp-content/uploads/2017/12/Pallet-Truck-Spares-1170x561.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2017/12/Pallet-Truck-Spares-270x129.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/roll-lift-pallet-truck/",
                "name": "Roll Lift Pallet Truck",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Roll/ Reel Carrying Pallet Trucks are designed to carry cylindrical shaped object, such as paper rolls, textile rolls and drums. With an average load capacity of 2000kg,</li>\n<li>Sloped ends allow for manually rolling material into position.</li>\n<li>V-shaped center holds rolls in position.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Roll Lift Pallet Trucks</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Capacity</td>\n<td width=\"324\"><strong>As Per Custom Requirement</strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Fork Length</strong></td>\n<td width=\"324\"><strong>As Per Custom Requirement</strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Overall Fork Width</strong></td>\n<td width=\"324\"><strong>As Per Custom Requirement</strong></td>\n</tr>\n<tr>\n<td width=\"198\">Lifting Height</td>\n<td width=\"324\">200mm</td>\n</tr>\n<tr>\n<td width=\"198\">Steering Wheels Size/ MOC</td>\n<td width=\"324\">180mm x 50mm \u2013 MS/Nylon/PU/ UHMW</td>\n</tr>\n<tr>\n<td width=\"198\">Load Roller Size/ MOC</td>\n<td width=\"324\">82mm x 70mm-\u00a0 MS/Nylon/PU/ UHMW</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Roll-Lift-Pallet-Truck.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Roll-Lift-Pallet-Truck.png 432w, https://www.kijeka.com/wp-content/uploads/2017/11/Roll-Lift-Pallet-Truck-300x203.png 300w, https://www.kijeka.com/wp-content/uploads/2017/11/Roll-Lift-Pallet-Truck-270x183.png 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Roll-Lift-Pallet-Truck.-KE303RL_Website-2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Roll-Lift-Pallet-Truck.-KE303RL_Website-2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/11/Roll-Lift-Pallet-Truck.-KE303RL_Website-2-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Roll-Lift-Pallet-Truck.-KE303RL_Website-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Roll-Lift-Pallet-Truck.-KE303RL_Website-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/11/Roll-Lift-Pallet-Truck.-KE303RL_Website-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/stainless-steel-pallet-truck/",
                "name": "Stainless Steel Pallet Truck",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Stainless Steel Frame &amp; Forks</strong>\u2013 Ideal for sanitary, pharmaceutical, medical, food, corrosive, and wet environments.</li>\n<li>Pallet Truck Made out from stainless steel 304 Grade Material for long life in the harshest environments.</li>\n<li>Ideal for corrosive environments.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td style=\"text-align: center;\" width=\"198\"><strong>Model</strong></td>\n<td width=\"324\"><strong>Stainless Steel Pallet Trucks\u00a0 </strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Standard Capacity </strong></td>\n<td width=\"324\"><strong>2500 kgs</strong></td>\n</tr>\n<tr>\n<td width=\"198\">Fork Length</td>\n<td width=\"324\">1150mm / 1220mm</td>\n</tr>\n<tr>\n<td width=\"198\">Overall Fork Width</td>\n<td width=\"324\">550mm / 685mm</td>\n</tr>\n<tr>\n<td width=\"198\">Size Of Fork</td>\n<td width=\"324\">150 x 65mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lower Fork Height</td>\n<td width=\"324\">90-100mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lifting Height</td>\n<td width=\"324\">200 mm</td>\n</tr>\n<tr>\n<td width=\"198\">Steering Wheels Size/ MOC</td>\n<td width=\"324\">180mm x 50mm \u2013 Polyurethane</td>\n</tr>\n<tr>\n<td width=\"198\">Load Roller Size/ MOC</td>\n<td width=\"324\">82mm x 70mm- Polyurethane</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Stainless-Steel-Pallet-Truck.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Stainless-Steel-Pallet-Truck.png 285w, https://www.kijeka.com/wp-content/uploads/2017/11/Stainless-Steel-Pallet-Truck-201x300.png 201w, https://www.kijeka.com/wp-content/uploads/2017/11/Stainless-Steel-Pallet-Truck-270x404.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/weighing-scale-pallet-truck/",
                "name": "Weighing Scale Pallet Truck",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Pallet truck scales, with built-in electronic weighing, which are reliable, easy to use, and suitable for harsh work conditions.</li>\n<li>These are essential for one who needs to weigh accurately but save time also.</li>\n<li>Pallet Truck Scale is a rugged and cost-effective solution and features a dependable terminal including a large, easily visible display and efficient keyboard. It is a perfect fit for any warehouse, where precise and mobile weighing is crucial.</li>\n</ul>\n<ul>\n<li>Rechargeable batteries, Charger built \u2013in.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Weighing Scale Pallet Truck\u00a0 </strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Capacity</td>\n<td width=\"324\">2000 kgs, 2500 Kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Length</td>\n<td width=\"324\">1150mm / 1220mm</td>\n</tr>\n<tr>\n<td width=\"198\">Overall Fork Width</td>\n<td width=\"324\">550mm / 685mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lower Fork Height</td>\n<td width=\"324\">90-100mm</td>\n</tr>\n<tr>\n<td width=\"198\">Lifting Height</td>\n<td width=\"324\">200mm</td>\n</tr>\n<tr>\n<td width=\"198\">Steering Wheels Size/ MOC</td>\n<td width=\"324\">180mm x 50mm \u2013 Nylon/PU</td>\n</tr>\n<tr>\n<td width=\"198\">Load Roller Size/ MOC</td>\n<td width=\"324\">82mm x 70mm- Nylon/PU</td>\n</tr>\n<tr>\n<td width=\"198\">Display</td>\n<td width=\"324\">6 Digits LED (Height \u2013 25mm)</td>\n</tr>\n<tr>\n<td width=\"198\">Display Designator</td>\n<td width=\"324\">On/ Off, Zero, Tare, Kg/LBS</td>\n</tr>\n<tr>\n<td width=\"198\">Power Source</td>\n<td width=\"324\">Rechargeable Battery, AC 110/2</td>\n</tr>\n<tr>\n<td width=\"198\">Load Cell</td>\n<td width=\"324\">Load Cell 4 Nos.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-2-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-2-scaled.jpg 2560w, https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-2-300x268.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-2-1024x915.jpg 1024w, https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-2-768x686.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-2-1536x1372.jpg 1536w, https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-2-2048x1830.jpg 2048w, https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-2-70x63.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-2-270x241.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-2-370x331.jpg 370w, https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-2-1170x1045.jpg 1170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/11/Weighing-Scale-Pallet-Truck.-KE-303WS-1-170x170.jpg 170w"
                    ]
                ]
            }
        ],
        "Polyurethane Wheels & Rollers": [
            {
                "link": "https://www.kijeka.com/product/polyurethane-rebonding-service/",
                "name": "Polyurethane Rebonding Service",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>You can save yourself time and money by having your existing wheels rebonded at our factory</strong></li>\n<li><strong>Rebonding is the greener more economical alternative to purchasing new wheels.</strong></li>\n<li>Re-cover your expensive wheel centers and save money.</li>\n<li><strong>Incoming Inspection:</strong> Wheels received for repair are identified, marked with unique customer designation and the polyurethane hardness is measured. We verify hub composition and can process steel, aluminum hubs.</li>\n<li><strong>Worn Urethane Removal: </strong>The old urethane is removed by applying just enough heat to break the adhesive bond between the urethane layer and the wheel hub. We never machine the old urethane off. Machining is faster, but you risk cutting into the wheel hub OD and damaging the hub integrity.</li>\n<li><strong>Cleaning and Shot peening:</strong> The wheel hubs are cleaned in an environmentally friendly bath to remove all grease, dirt, and other contaminants and the wheels are blasted. The steel shot reduces surface stress and cleans the metal, leaving no residue to interfere with the adhesive bond.</li>\n<li><strong>Adhesive Application:</strong> We have a selection of wheel adhesives that match the wheel\u2019s required performance. For high speed amusement rides and heavy load industrial applications we will apply two layers of adhesive to prevent premature bond failure. The adhesive is applied in a controlled atmosphere free of contaminants.</li>\n<li><strong>Polyurethane Selection:</strong> Based on their experience with thousands of wheels, our technicians choose the best Polyurethane and specific Wheel Hardness for your application. Some incoming wheels have signs of premature wear and/or heat damage. In those cases we will contact you to discuss the exact nature of on your application. We may recommend an increase in wheel diameter or urethane hardness. Either will increase load capacity.</li>\n<li><strong>Polyurethane Casting and Curing: </strong>After the adhesive is applied to the wheel hub OD, we mix the chosen polyurethane prepolymer with a curative and the mixture is poured into a mold with the hub at its center. Great care is taken to prevent either air or water from becoming part of the mix.</li>\n<li>Industrial Wheels cures the polyurethane in convection ovens from 1 hour to 16 hours depending on the type of polyurethane. Convection curing increases the performance properties and life of the wheel.</li>\n<li>After curing, each wheel is visually inspected for air bubbles or contaminants in the urethane and we make sure there are no gaps between the polyurethane and the hub.</li>\n<li><strong>Machining and Inspection: </strong>We manually machine the outer diameter of each wheel and can accommodate customer requests for; specific urethane thicknesses, side cuts, grooves, or concave or convex OD shapes.</li>\n<li>Each wheel is dimensionally inspected and the polyurethane hardness checked prior to shipment.</li>\n</ul>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img19.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img19.png 474w, https://www.kijeka.com/wp-content/uploads/2017/11/img19-300x161.png 300w, https://www.kijeka.com/wp-content/uploads/2017/11/img19-270x145.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/polyurethane-tractiondrive-wheels/",
                "name": "Polyurethane Traction/Drive Wheels",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Top quality Drive wheels for drums, machinery, bridges, conveyors, drive units, water purification plants.</li>\n<li><strong>Our traction wheels are made \u200b\u200bfrom a cast iron or steel core</strong> with PU hardness 92 \u00b0 Shore A. Temperature range : -40 \u00b0 C to +85 \u00b0 C, Extremely durable, high load capacity and with a plain \u00a0bore, Bearing or with keyway</li>\n<li>Drive wheels Made of high quality elastomeric polyurethane , quiet operation, good surface preservation, high abrasion resistance, resists nicks and cracks, very good chemical connection with the wheel, Minimal turn and rolling resistance, Small thickness: minimum risk of compression and deformation, even with long downtimes and high loads, Leaves no markes, Resistant to oils, greases and many chemicals. Shock resistant and sound absorbing.</li>\n<li><strong>We can manufacture from a supplied sample or technical drawings.</strong></li>\n</ul>\n<p>\u00a0</p>\n<table width=\"601\">\n<tbody>\n<tr>\n<td width=\"162\"><strong><center>Model</center></strong></td>\n<td width=\"439\"><strong>Polyurethane Traction/Drive Wheels</strong></td>\n</tr>\n<tr>\n<td width=\"162\">Size range</td>\n<td width=\"439\">As Per Customer Sample or Technical Drawings</td>\n</tr>\n<tr>\n<td width=\"162\">Available Core Type</td>\n<td width=\"439\">Aluminium, Mild Steel, Stainless Steel</td>\n</tr>\n<tr>\n<td width=\"162\">Available Bearing Option</td>\n<td width=\"439\">Plain bore , Bearing or with keyway as per Requirement</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img17.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img17.png 580w, https://www.kijeka.com/wp-content/uploads/2017/11/img17-300x142.png 300w, https://www.kijeka.com/wp-content/uploads/2017/11/img17-270x128.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/polyurethane-wheels/",
                "name": "Polyurethane Wheels",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Polyurethane (PU) wheels are a unique product that offers the elasticity of rubber wheels combined with the toughness and durability of metal wheels. This makes polyurethane the perfect tread for transportation wheels, traction wheels and guiding rollers.</li>\n</ul>\n<ul>\n<li>Urethanes wheels have better abrasion and tear resistance than rubber wheels, while offering higher load bearing capacity.</li>\n<li>Compared to plastic wheels, urethane wheels offer superior impact resistance, while offering excellent wear properties and elastic memory.</li>\n<li>Urethane is available in a broad Shore hardness range, depending of surface, load capacity and preferred rolling conditions the Shore hardness be chosen to fit the application</li>\n<li>Polyurethane wheels are chosen by engineers as a replacement for rubber, plastic and metal wheels because Abrasion Resistant, Oil &amp; Solvent resistant, Good Load Bearing Capacity, Tear Resistant, Weather resistant, Heat &amp; Cold Resistant, Excellent Noise abatement Properties</li>\n</ul>\n<p><strong>\u00a0</strong></p>\n<table width=\"601\">\n<tbody>\n<tr>\n<td width=\"162\"><center>Model</center></td>\n<td width=\"439\"><strong>Polyurethane Wheels </strong></td>\n</tr>\n<tr>\n<td width=\"162\">Size range</td>\n<td width=\"439\">From 50 mm O.D. to 300 mm O.D. Or Customize As per requirement</td>\n</tr>\n<tr>\n<td width=\"162\">Load carrying capacity</td>\n<td width=\"439\">From 40 Kgs to 1500 Kgs.</td>\n</tr>\n<tr>\n<td width=\"162\">Available Core Type</td>\n<td width=\"439\">PPCP, Cast Iron, Aluminium, Mild Steel, Stainless Steel.</td>\n</tr>\n<tr>\n<td width=\"162\">Available Bearing Option</td>\n<td width=\"439\">Plain bore / ball bearing / needle roller bearing / SS or MS Insert</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/polyurethane-wheels.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/polyurethane-wheels.png 272w, https://www.kijeka.com/wp-content/uploads/2017/11/polyurethane-wheels-70x58.png 70w, https://www.kijeka.com/wp-content/uploads/2017/11/polyurethane-wheels-270x222.png 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/polyurethane-wheels2-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/polyurethane-wheels2-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/11/polyurethane-wheels2-170x170.png 170w"
                    ]
                ]
            }
        ],
        "Wheels & Casters": [
            {
                "link": "https://www.kijeka.com/product/casters/",
                "name": "Casters",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>We design\u00a0casters\u00a0to meet every load requirement and application environment from furniture wheels to industrial casters; including\u00a0light duty,\u00a0medium duty\u00a0or\u00a0extra heavy duty.</li>\n</ul>\n<p><strong>\u00a0</strong></p>\n<table width=\"601\">\n<tbody>\n<tr>\n<td width=\"162\"><center><strong>Model</strong></center></td>\n<td width=\"439\"><strong>Casters</strong></td>\n</tr>\n<tr>\n<td width=\"162\"><strong>Caster MOC</strong></td>\n<td width=\"439\"><strong>Steel , Stainless Steel </strong></td>\n</tr>\n<tr>\n<td width=\"162\"><strong>Caster Type</strong></td>\n<td width=\"439\">Fix Type, Swivel Type, Brake Type \u00a0Scaffolding Caster, <em>Threaded Stem</em>\u00a0Casters, Spring Loaded Casters, Stainless Steel Caster, Medical Equipment Casters, Light, Medium, Heavy Duty Casters</td>\n</tr>\n<tr>\n<td width=\"162\">Size range</td>\n<td width=\"439\">From 50 mm O.D. to 250 mm O.D.</td>\n</tr>\n<tr>\n<td width=\"162\">Load carrying capacity</td>\n<td width=\"439\">From 40 Kgs to 1000 Kgs.</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img14.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img14.png 540w, https://www.kijeka.com/wp-content/uploads/2017/11/img14-210x300.png 210w, https://www.kijeka.com/wp-content/uploads/2017/11/img14-270x386.png 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img15-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img15-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/11/img15-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/wheels/",
                "name": "Wheels",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>We design\u00a0wheels\u00a0to meet every load requirement and application environment from furniture wheels to industrial casters; including\u00a0light duty,\u00a0medium duty\u00a0or\u00a0extra heavy duty.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"601\">\n<tbody>\n<tr>\n<td width=\"162\"><strong><center>Model</center> </strong></td>\n<td width=\"439\"><strong>Wheels </strong></td>\n</tr>\n<tr>\n<td width=\"162\">Size range</td>\n<td width=\"439\">Size range: From 50 mm O.D. to 300 mm O.D.</td>\n</tr>\n<tr>\n<td width=\"162\">Load carrying capacity</td>\n<td width=\"439\">From 40 Kgs to 2000 Kgs.</td>\n</tr>\n<tr>\n<td width=\"162\"><strong>Available Wheels MOC</strong></td>\n<td width=\"439\"><strong>PPCP, Nylon , Polyurethane, Cast Iron , Mild Steel, Stainless Steel, Pneumatic Wheels </strong></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img12-1.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img12-1.png 487w, https://www.kijeka.com/wp-content/uploads/2017/11/img12-1-300x197.png 300w, https://www.kijeka.com/wp-content/uploads/2017/11/img12-1-270x177.png 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img13-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/img13-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/11/img13-170x170.png 170w"
                    ]
                ]
            }
        ],
        "Stackers": [
            {
                "link": "https://www.kijeka.com/product/counterbalance-fully-powered-drum-stacker/",
                "name": "Counterbalance Fully Powered Drum Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Drum stackers provide a safe, ergonomic solution for your most challenging Drum stacking needs.</li>\n<li>Counterbalance Drum Stackers are specifically designed to provide precise Drum handling and maneuverability.</li>\n<li>Horizontal movement over large distances, as well as stacking, our stand-on Drum stackers are ideal.</li>\n<li>Counterbalance design allows close access to loading and unloading areas.</li>\n<li>Their heavy-duty construction will provide years of dependable service.</li>\n<li>Eagle-grip design provide safest griping on Drum.</li>\n<li>Operating Type: Battery Operated Walking, Lifting, Stacking&amp; Up-Down.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Transporting, and Stacking of Drums.</li>\n<li>Frequent loading and unloading of Drums.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td><strong>Counterbalance Powered Drum stacker</strong></td>\n</tr>\n<tr>\n<td>Drive Type</td>\n<td>/</td>\n<td>Electric (Battery Driven)</td>\n</tr>\n<tr>\n<td>Operating Type</td>\n<td>/</td>\n<td>Standing steer type</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>420</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>2400 from Drum Bottom</td>\n</tr>\n<tr>\n<td>Total height</td>\n<td>mm</td>\n<td>1860</td>\n</tr>\n<tr>\n<td>Total length</td>\n<td>mm</td>\n<td>2270</td>\n</tr>\n<tr>\n<td>Total width</td>\n<td>mm</td>\n<td>1170</td>\n</tr>\n<tr>\n<td>Turning radius</td>\n<td>mm</td>\n<td>2150</td>\n</tr>\n<tr>\n<td>Max. Grade ability\n<p>(Fully-loaded/no-load)</p></td>\n<td>%</td>\n<td>3/5</td>\n</tr>\n<tr>\n<td>Driving wheel size</td>\n<td>mm</td>\n<td>\u00d8250*80</td>\n</tr>\n<tr>\n<td>Tire</td>\n<td>/</td>\n<td>Polyurethane</td>\n</tr>\n<tr>\n<td>Brake type</td>\n<td>/</td>\n<td>Electromagnetic braking</td>\n</tr>\n<tr>\n<td>Drive motor power</td>\n<td>kw</td>\n<td>1.2</td>\n</tr>\n<tr>\n<td>Lifting motor power</td>\n<td>kw</td>\n<td>2.2</td>\n</tr>\n<tr>\n<td>Noise level</td>\n<td>db(A)</td>\n<td>\uff1c70</td>\n</tr>\n<tr>\n<td>Battery\u00a0voltage/capacity</td>\n<td>V/Ah</td>\n<td>24/210</td>\n</tr>\n<tr>\n<td>Charger</td>\n<td>V/A</td>\n<td>24/30</td>\n</tr>\n<tr>\n<td>Net weight</td>\n<td>kg</td>\n<td>990</td>\n</tr>\n</tbody>\n</table>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker_full.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker_full.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker_full-300x279.jpg 300w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker_full-768x713.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker_full-70x65.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker_full-270x251.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker_full-370x344.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker1-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker2-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker3-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker3-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-fully-powered-drum-stacker3-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/counterbalance-semi-powered-drum-stacker/",
                "name": "Counterbalance Semi Powered Drum Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Drum stackers provide a safe, ergonomic solution for your most challenging Drum stacking needs.</li>\n<li>Counterbalance Drum Stackers are specifically designed to provide precise Drum handling and maneuverability.</li>\n<li>Counterbalance design allows close access to loading and unloading areas</li>\n<li>Eagle-grip design provide safest griping on Drum</li>\n<li>Operating Type: Battery Operated Walking, Lifting, Stacking&amp; Up-Down</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Transporting, and Stacking of Drums.</li>\n<li>Frequent loading and unloading of Drums</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\" style=\"text-align: center;\"><strong>Model</strong></td>\n<td>\n<p style=\"text-align: left;\"><strong>Counterbalance Powered Drum stacker</strong></p>\n</td>\n</tr>\n<tr>\n<td>Operating Type</td>\n<td>/</td>\n<td>Manual Propel/Battery Operated Up-Down</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>280</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>1100 from Drum Bottom</td>\n</tr>\n<tr>\n<td>Total height</td>\n<td>mm</td>\n<td>1880</td>\n</tr>\n<tr>\n<td>Total length</td>\n<td>mm</td>\n<td>1300</td>\n</tr>\n<tr>\n<td>Total width</td>\n<td>mm</td>\n<td>810</td>\n</tr>\n<tr>\n<td>Turning radius</td>\n<td>mm</td>\n<td>1820</td>\n</tr>\n<tr>\n<td>Driving wheel size</td>\n<td>mm</td>\n<td>\u00d8125*50</td>\n</tr>\n<tr>\n<td>Battery</td>\n<td>Ah/V</td>\n<td>120Ah 12V</td>\n</tr>\n<tr>\n<td>Tire</td>\n<td>/</td>\n<td>Polyurethane</td>\n</tr>\n<tr>\n<td>Net weight</td>\n<td>kg</td>\n<td>270</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker-232x300.jpg 232w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker-768x994.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker-791x1024.jpg 791w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker-70x90.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker-270x349.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker-370x480.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker1-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker2-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker3-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker3-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker3-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker4-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker4-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Counterbalance-semi-powered-drum-stacker4-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/electric-reach-stacker/",
                "name": "Electric Reach Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>These reach stacker lift trucks are designed for indoor use and ideally suited for a wide variety of applications such as dock operations, general warehouse and storage, home improvement warehouses, and paint and chemical distribution.</li>\n<li>Best Option for your material handling jobs include unloading or loading trailers, dockside manoeuvring, or stocking,</li>\n<li>The Reach Stacker line of motorized pallet trucks gives you big capacity and productivity with the operational cost of a walkie rather than a rider. And our superior ergonomics along with the versatility of user selectable performance modes will help to increase your productivity.</li>\n<li>The heavy-duty walkie stacker series features a tough, unitized construction that is robotically welded, for superior reliability.</li>\n<li>Best quality lifting Motor, hydraulic power unit, an operating handle, power plug, power display</li>\n<li>Electric power Steering System, High Storage Battery ensures Strong and Long Lasting Power</li>\n<li>The Braking system combines magnetic Brake &amp; regenerative Brake, greatly prolongs the using lift of friction plate</li>\n<li>Ergonomic Operation with Emergency stop switch, Lock Button &amp; Multi-valve Controlling levers</li>\n<li>Simple &amp; Convenient operation system</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td style=\"text-align: center;\" width=\"222\"><strong>Model</strong></td>\n<td width=\"300\"><strong>Electric Reach Stacker </strong></td>\n</tr>\n<tr>\n<td width=\"222\">MOC</td>\n<td width=\"300\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"222\">Drive Type</td>\n<td width=\"300\">Electric</td>\n</tr>\n<tr>\n<td width=\"222\">Loading Capacity</td>\n<td width=\"300\">1500 kgs</td>\n</tr>\n<tr>\n<td width=\"222\">Load Center</td>\n<td width=\"300\">500mm</td>\n</tr>\n<tr>\n<td width=\"222\">Wheels Type</td>\n<td width=\"300\">Polyurethane</td>\n</tr>\n<tr>\n<td width=\"222\">Front Wheel Dimension</td>\n<td width=\"300\">180 x 50mm</td>\n</tr>\n<tr>\n<td width=\"222\">Rear Wheel Dimension</td>\n<td width=\"300\">130 x 55mm</td>\n</tr>\n<tr>\n<td width=\"222\">Traction Wheels</td>\n<td width=\"300\">230 x 75mm</td>\n</tr>\n<tr>\n<td width=\"222\">Ground Clearance</td>\n<td width=\"300\">45 mm</td>\n</tr>\n<tr>\n<td width=\"222\">Reach Distance</td>\n<td width=\"300\">590mm</td>\n</tr>\n<tr>\n<td width=\"222\"><strong>Available Lifting Height</strong></td>\n<td width=\"300\"><strong>2500mm, 3000mm, 3500mm, 4000mm,\u00a0</strong><strong>4500mm</strong></td>\n</tr>\n<tr>\n<td width=\"222\"><strong>Fork Clearance from the ground</strong></td>\n<td width=\"300\"><strong>35 mm</strong></td>\n</tr>\n<tr>\n<td width=\"222\"><strong>Fork Dimension </strong></td>\n<td width=\"300\"><strong>920x100x35 mm</strong></td>\n</tr>\n<tr>\n<td width=\"222\"><strong>Fork Adjustable </strong></td>\n<td width=\"300\"><strong>200-620 mm</strong></td>\n</tr>\n<tr>\n<td width=\"222\"><strong>Fork tilt forward/Back</strong></td>\n<td width=\"300\"><strong>2/4</strong></td>\n</tr>\n<tr>\n<td width=\"222\">Lifting Speed (lade &amp; Unlade)</td>\n<td width=\"300\"><strong>150/ 100 mm/sec</strong></td>\n</tr>\n<tr>\n<td width=\"222\">Lowering Speed(lade &amp; Unlade)</td>\n<td width=\"300\"><strong>500 mm/sec</strong></td>\n</tr>\n<tr>\n<td width=\"222\">Traction Speed (lade &amp; Unlade)</td>\n<td width=\"300\"><strong>6/5- Km/h</strong></td>\n</tr>\n<tr>\n<td width=\"222\">Traction Motor</td>\n<td width=\"300\">1.5KW</td>\n</tr>\n<tr>\n<td width=\"222\"><strong>Lift Motor</strong></td>\n<td width=\"300\"><strong>3 KW</strong></td>\n</tr>\n<tr>\n<td width=\"222\"><strong>Battery Volts/Ampere</strong></td>\n<td width=\"300\"><strong>2Vx12/270</strong></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Electric-Reach-Stacker.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Electric-Reach-Stacker.png 311w, https://www.kijeka.com/wp-content/uploads/2017/11/Electric-Reach-Stacker-258x300.png 258w, https://www.kijeka.com/wp-content/uploads/2017/11/Electric-Reach-Stacker-270x314.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/flameproof-electric-drum-stacker/",
                "name": "Flameproof Electric Drum Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Drum Stacker with Flameproof AC Power Pack</strong></li>\n<li><strong>Can be supplied in both zone 1 and zone 2 flameproof protection, Stackers are for internal use only and can be used in warehouse and manufacturing areas.</strong></li>\n<li>Drive Type: Manual Push-Pull Type, FLP-Electrical- Hydraulic Up-Down</li>\n<li>MOC: MS Powder Coated Finish Or Paint</li>\n<li><strong>Standard Capacity: 500 kgs</strong></li>\n<li><strong>Structure Design: </strong>Single Mast / Double Mast/ Triple Mast</li>\n<li><strong>Lifting Height: </strong>1600mm Standard, 2000mm, 2500mm, 3000mm</li>\n</ul>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Stacker_Flame-Proof-Electrical-6-copy-scaled.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Stacker_Flame-Proof-Electrical-6-copy-scaled.jpg 1779w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Stacker_Flame-Proof-Electrical-6-copy-209x300.jpg 209w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Stacker_Flame-Proof-Electrical-6-copy-712x1024.jpg 712w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Stacker_Flame-Proof-Electrical-6-copy-768x1105.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Stacker_Flame-Proof-Electrical-6-copy-1068x1536.jpg 1068w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Stacker_Flame-Proof-Electrical-6-copy-1423x2048.jpg 1423w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Stacker_Flame-Proof-Electrical-6-copy-63x90.jpg 63w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Stacker_Flame-Proof-Electrical-6-copy-243x350.jpg 243w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Stacker_Flame-Proof-Electrical-6-copy-334x480.jpg 334w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Stacker_Flame-Proof-Electrical-6-copy-1170x1683.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2020/05/Drum-Stacker_Flame-Proof-Electrical-6-copy-270x388.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/flameproof-electric-stacker/",
                "name": "Flameproof Electric Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Stacker with Flameproof AC Power Pack</li>\n<li>Can be supplied in both zone 1 and zone 2 flameproof protection, Stackers are for internal use only and can be used in warehouse and manufacturing areas.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Flameproof Electric Stacker </strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Capacity</td>\n<td width=\"324\">1000 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Load Center</td>\n<td width=\"324\">600mm</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Length</td>\n<td width=\"324\">1150 mm</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Width</td>\n<td width=\"324\">550/600/ 300-850 mm (Adjustable Fork)</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Structure Design </strong></td>\n<td width=\"324\"><strong>Single Mast / Double Mast/ Triple Mast </strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Lifting Height</strong></td>\n<td width=\"324\"><strong>1600mm Standard, 2000mm, 2500mm, 3000mm, </strong>\n<p><strong>4000mm, 4500mm</strong></p></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Available Capacities </strong></td>\n<td width=\"324\"><strong>500 Kgs, 1000 Kgs, 1500 Kgs </strong></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Flameproof-Electric-Stacker.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Flameproof-Electric-Stacker.png 258w, https://www.kijeka.com/wp-content/uploads/2017/11/Flameproof-Electric-Stacker-153x300.png 153w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/full-electric-stacker/",
                "name": "Full Electric Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>The Full Electric Stacker with different loading capacities and various lifting heights is built for stacking in intensive applications in stores and factories, applications that require durable high capacity trucks that are also capable of horizontal transport purposes.</li>\n<li>Most advanced AC Driving motor &amp; Controller using to ensure the smooth running of Precise, vehicle with regenerative braking ramp, anti slip, Maintenance free motor function</li>\n<li>Best quality lifting Motor, hydraulic power unit, an operating handle, power plug, power display</li>\n<li>Suspension design drive system, ensure the good ground contact with the wheels</li>\n<li>Handy Steering with Handle Controller ensure comfortable operation</li>\n<li>Design puts the focus on the safety &amp; ergonomic working condition of the user.</li>\n<li>Open able integrated rear cover board, Accurate Display of power meter, fault code Display when the Stacker Failure which gives convenient maintenance</li>\n<li>Simple &amp; Convenient operation system</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Full Electric Stacker </strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Electric ( Fully Battery Operated)</td>\n</tr>\n<tr>\n<td width=\"198\">Load Center</td>\n<td width=\"324\">500mm</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Structure Design </strong></td>\n<td width=\"324\"><strong>Single Mast / Double Mast </strong></td>\n</tr>\n<tr>\n<td width=\"198\">Available\u00a0 Capacity</td>\n<td width=\"324\">1000Kgs/1500Kgs/2000Kgs.</td>\n</tr>\n<tr>\n<td width=\"198\">Available Lifting Height</td>\n<td width=\"324\">1600 mm,\u00a0 2000mm, 2500mm,3000mm, 3300mm\n<p>4000mm,</p></td>\n</tr>\n<tr>\n<td width=\"198\">Fork Length</td>\n<td width=\"324\">1150 x160 x50mm</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Lower Height</td>\n<td width=\"324\">80-90mm</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Width</td>\n<td width=\"324\">360-680 mm (Adjustable Fork)</td>\n</tr>\n<tr>\n<td width=\"198\">Traction Motor</td>\n<td width=\"324\">1.5KW</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Lift Motor</strong></td>\n<td width=\"324\"><strong>2.2 KW/ 3 KW</strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Battery Charger Input</strong></td>\n<td width=\"324\"><strong>AC-220V/ 50(60)HZ</strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Battery Charger Output</strong></td>\n<td width=\"324\"><strong>DC- 24V/40A</strong></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Fully-Electric-Stacker.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Fully-Electric-Stacker.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/11/Fully-Electric-Stacker-254x300.jpg 254w, https://www.kijeka.com/wp-content/uploads/2017/11/Fully-Electric-Stacker-768x907.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/11/Fully-Electric-Stacker-867x1024.jpg 867w, https://www.kijeka.com/wp-content/uploads/2017/11/Fully-Electric-Stacker-70x83.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/11/Fully-Electric-Stacker-270x319.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/11/Fully-Electric-Stacker-370x437.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/fully-powered-drum-stacker/",
                "name": "Fully Powered Drum Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Drum stackers provide a safe, ergonomic solution for your most challenging Drum stacking needs.</li>\n<li>Horizontal movement over large distances, as well as stacking</li>\n<li>Available to carry the drum to rack lower than 2400mm</li>\n<li>Their heavy-duty construction will provide years of dependable service</li>\n<li>Eagle-grip design provide safest griping on Drum.</li>\n<li>Operating Type: Battery Operated Walking, Lifting, Stacking &amp; Up-Down.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Transporting, and Stacking of Drums.</li>\n<li>Frequent loading and unloading of Drums.</li>\n</ul>\n<p>\u00a0</p>\n<table style=\"height: 1018px;\" width=\"639\">\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td><strong>Counterbalance Powered Drum stacker</strong></td>\n</tr>\n<tr>\n<td>Drive Type</td>\n<td>/</td>\n<td>Electric(Battery Driven)</td>\n</tr>\n<tr>\n<td>Operating Type</td>\n<td>/</td>\n<td>Standing steer type</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>600</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>2400 from Drum Bottom</td>\n</tr>\n<tr>\n<td>Turning radius</td>\n<td>mm</td>\n<td>1710</td>\n</tr>\n<tr>\n<td>Max. Grade ability\n<p>(Fully-loaded/no-load)</p></td>\n<td>%</td>\n<td>3/5</td>\n</tr>\n<tr>\n<td>Driving wheel size</td>\n<td>mm</td>\n<td>\u00d8250*80</td>\n</tr>\n<tr>\n<td>Tire</td>\n<td>/</td>\n<td>Polyurethane</td>\n</tr>\n<tr>\n<td>Brake type</td>\n<td>/</td>\n<td>Electromagnetic braking</td>\n</tr>\n<tr>\n<td>Drive motor power</td>\n<td>kw</td>\n<td>1.2</td>\n</tr>\n<tr>\n<td>Lifting motor power</td>\n<td>kw</td>\n<td>2.2</td>\n</tr>\n<tr>\n<td>Noise level</td>\n<td>db(A)</td>\n<td>\uff1c70</td>\n</tr>\n<tr>\n<td>Battery\u00a0voltage/capacity</td>\n<td>V/Ah</td>\n<td>24/210</td>\n</tr>\n<tr>\n<td>Charger</td>\n<td>V/A</td>\n<td>24/30</td>\n</tr>\n<tr>\n<td>Net weight</td>\n<td>kg</td>\n<td>635</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker2.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker2.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker2-262x300.jpg 262w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker2-768x879.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker2-895x1024.jpg 895w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker2-70x80.jpg 70w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker2-270x309.jpg 270w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker2-370x423.jpg 370w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker1-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker3-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker3-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Fully-Powered-Drum-Stacker3-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/hook-stacker/",
                "name": "Hook Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Hook Stacker with Boom type hook arrangement for rolls / coil handling as well as pallet handling.</strong></li>\n<li><strong>Lifting Height: </strong>1500mm</li>\n<li>Loading Capacity: 500kgs</li>\n<li>Drive Type: \u00a0Manual Push-Pull Type, Hydraulic Up-Down</li>\n<li><b><b>Available Option: </b></b>Customize Lifting Height, Capacity, Drive option Like Manual-Hydraulic, FLP/ Non-FLP Electric Operated, Battery Operated Up-Down</li>\n<li>Best Product in India</li>\n</ul>\n<p>\u00a0</p>\n<p>\u00a0</p>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Hook-Stacker_Website.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2020/05/Hook-Stacker_Website.jpg 869w, https://www.kijeka.com/wp-content/uploads/2020/05/Hook-Stacker_Website-255x300.jpg 255w, https://www.kijeka.com/wp-content/uploads/2020/05/Hook-Stacker_Website-768x903.jpg 768w, https://www.kijeka.com/wp-content/uploads/2020/05/Hook-Stacker_Website-70x82.jpg 70w, https://www.kijeka.com/wp-content/uploads/2020/05/Hook-Stacker_Website-270x318.jpg 270w, https://www.kijeka.com/wp-content/uploads/2020/05/Hook-Stacker_Website-370x435.jpg 370w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/hydraulic-roller-stacker/",
                "name": "Hydraulic Roller Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li><strong>Roller Stacker is ideal for handling anything which rolls and required to lift.</strong></li>\n<li>Having Conveyor system for rolling of Drum, dies, Paper/ Plastic Rolls, Molds, etc..</li>\n<li><strong>Rolls anything off the floor or pallet, transports to destination, lifts to the required height and rolls where required.</strong></li>\n<li><strong>Best Option for Vertical Drum Loading/Unloading from the vehicle</strong></li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Hydraulic Roller Stacker \u00a0\u00a0</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Capacity</td>\n<td width=\"324\">500 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Platform Sizes</td>\n<td width=\"324\">\u00b7\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 700mm Length x 600mm Width\n<p>\u00b7\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 900mm Length x 700mm Width</p></td>\n</tr>\n<tr>\n<td width=\"198\">Lower Fork Height</td>\n<td width=\"324\">110 mm</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Structure Design </strong></td>\n<td width=\"324\"><strong>Single Mast / Double Mast </strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Lifting Height</strong></td>\n<td width=\"324\"><strong>1600mm Standard, 2000mm, 2500mm, 3000mm</strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Available Capacities </strong></td>\n<td width=\"324\"><strong>1000 kgs, 1500 Kgs </strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Available Drive Option</strong></td>\n<td width=\"324\"><strong>Manual-Hydraulic, Electric Operated, </strong>\n<p><strong>Battery Operated Up-Down</strong></p></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Hydraulic-Roller-Stacker.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Hydraulic-Roller-Stacker.png 294w, https://www.kijeka.com/wp-content/uploads/2017/11/Hydraulic-Roller-Stacker-202x300.png 202w, https://www.kijeka.com/wp-content/uploads/2017/11/Hydraulic-Roller-Stacker-270x401.png 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/manual-drum-stacker/",
                "name": "Manual Drum Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Manual Drum Stacker is designed to raise and place a drum at required Location.</li>\n<li>Available to carry the drum to stack lower than 1500 mm.</li>\n<li>Eagle-grip design provide safest griping on Steel/HDPE Plastic Drums.</li>\n<li>Loading Capacity: 400 Kgs.</li>\n<li>Operating Type: Manual Propel , Eagle-grip Drum Holding,\u00a0 Hydraulically Up-Down.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Transporting, and Stacking of.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td>\n<p style=\"text-align: left;\"><strong>Manual Drum Stacker. </strong></p>\n</td>\n</tr>\n<tr>\n<td>Operating Type</td>\n<td>/</td>\n<td>Manual Propel/Hydraulically Up-Down</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>400</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>1500 from Drum Bottom</td>\n</tr>\n<tr>\n<td>Inner/Outer Width of Front Leg</td>\n<td>mm</td>\n<td>630/810</td>\n</tr>\n<tr>\n<td>Turning radius</td>\n<td>mm</td>\n<td>1400</td>\n</tr>\n<tr>\n<td>wheel size</td>\n<td>mm</td>\n<td>\u00d8150*50</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker2.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker2.jpg 800w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker2-196x300.jpg 196w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker2-768x1177.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker2-668x1024.jpg 668w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker2-59x90.jpg 59w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker2-228x350.jpg 228w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker2-313x480.jpg 313w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker2-270x414.jpg 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker1-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker1-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker1-170x170.jpg 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker3-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker3-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker3-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/manual-drum-stacker-v-shaped-base/",
                "name": "Manual Drum Stacker (V-Shaped Base)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Manual Drum Stacker with V-Shaped Base Frame raise and place a drum at required Location.</li>\n<li>Available to carry the drum to stack lower than 1500 mm.</li>\n<li>Eagle-grip Clamping Mechanism provide safest griping on Steel/HDPE Pl.astic Drums.</li>\n<li>Loading Capacity: 450 Kgs.</li>\n<li>Operating Type: Manual Propel , Eagle-grip Drum Holding,\u00a0 Hydraulically\u00a0 Up-Down.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Transporting, Stacking, Palletizing of\u00a0Drums.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td><strong>Manual Drum Stacker\u00a0</strong><strong>(V-Shaped Base). </strong></td>\n</tr>\n<tr>\n<td>Operating Type</td>\n<td>/</td>\n<td>Manual Propel/Hydraulically Up-Down</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>450</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>1100 from Drum Bottom</td>\n</tr>\n<tr>\n<td>Inner/Outer Width of Front Leg</td>\n<td>mm</td>\n<td>920/1140</td>\n</tr>\n<tr>\n<td>Turning radius</td>\n<td>mm</td>\n<td>1100</td>\n</tr>\n<tr>\n<td>wheel size</td>\n<td>mm</td>\n<td>\u00d8150*50/ \u00d8125*50</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker-V-Shaped-Base.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker-V-Shaped-Base.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker-V-Shaped-Base-186x300.jpg 186w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker-V-Shaped-Base-768x1241.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker-V-Shaped-Base-634x1024.jpg 634w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker-V-Shaped-Base-56x90.jpg 56w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker-V-Shaped-Base-217x350.jpg 217w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker-V-Shaped-Base-297x480.jpg 297w, https://www.kijeka.com/wp-content/uploads/2017/06/Manual-Drum-Stacker-V-Shaped-Base-270x436.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/manual-hydraulic-stacker/",
                "name": "Manual Hydraulic Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Pallet stackers/ Manual Stackers are a step up from the traditional Pallet Truck</li>\n<li>Manual Hydraulic Stackers make moving, lifting, loading and unloading simpler and quicker.</li>\n<li>Manual Stackers are an economical alternative to a forklift truck and \u2013 because of their smaller size and weight \u2013 can be used in smaller spaces.</li>\n<li>Ideal for warehousing and light manufacturing applications.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Manual Hydraulic Stacker \u00a0\u00a0</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Capacity</td>\n<td width=\"324\">1000 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Length</td>\n<td width=\"324\">1150mm</td>\n</tr>\n<tr>\n<td width=\"198\">Overall Fork Width</td>\n<td width=\"324\">550mm /600mm /300-850mm Adjustable</td>\n</tr>\n<tr>\n<td width=\"198\">Lower Fork Height</td>\n<td width=\"324\">90-100mm</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Structure Design </strong></td>\n<td width=\"324\"><strong>Single Mast / Double Mast </strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Lifting Height</strong></td>\n<td width=\"324\"><strong>1600mm Standard, 2000mm, 2500mm, 3000mm</strong></td>\n</tr>\n<tr>\n<td width=\"198\">Structure Design</td>\n<td width=\"324\">Single Mast / Double Mast</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Available Capacities</strong></td>\n<td width=\"324\"><strong>1000 kgs, 1500 Kgs , 2000 Kgs</strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Other Option </strong></td>\n<td width=\"324\"><strong>\u00a0 Special fork length, width, wheels &amp; capacity </strong>\n<p><strong>\u00a0 As per Client Requirement.</strong></p></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Available Drive Option</strong></td>\n<td width=\"324\"><strong>Manual-Hydraulic, Electric Operated, </strong>\n<p><strong>Battery Operated Up-Down</strong></p></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Stacker.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Stacker.jpg 868w, https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Stacker-223x300.jpg 223w, https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Stacker-768x1035.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Stacker-760x1024.jpg 760w, https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Stacker-67x90.jpg 67w, https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Stacker-260x350.jpg 260w, https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Stacker-356x480.jpg 356w, https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Stacker-270x364.jpg 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Hydraulic-Stacker-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Hydraulic-Stacker-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Hydraulic-Stacker-170x170.png 170w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Stacker.KE300M-2-CRM-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Stacker.KE300M-2-CRM-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/11/Manual-Stacker.KE300M-2-CRM-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/paper-reel-stacker/",
                "name": "Paper Reel Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Ideal for handling Plastic Rolls, Paper Rolls, Cloth Rolls Etc\u2026</li>\n<li>Safe, effective, fast way of transporting, lifting, stacking, loading, unloading Paper, Plastic Roll/Reels</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Paper Reel Stacker </strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Capacity</td>\n<td width=\"324\">500 Kgs, 1000 Kgs, 1500 Kgs, 2000 Kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Min. Lifting Height</td>\n<td width=\"324\">120 mm</td>\n</tr>\n<tr>\n<td width=\"198\">Max. Lifting Height</td>\n<td width=\"324\"><strong>500 mm to 6000 mm</strong></td>\n</tr>\n<tr>\n<td width=\"198\">Top Platform Size</td>\n<td width=\"324\">600/700/1000 mm</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Structure Design </strong></td>\n<td width=\"324\"><strong>Single Mast / Double Mast /Triple Mast</strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Available Drive Option</strong></td>\n<td width=\"324\"><strong>Manual-Hydraulic, Electric Operated, </strong>\n<p><strong>Battery Operated Up-Down</strong></p></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Paper-Reel-Stacker.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Paper-Reel-Stacker.jpg 1219w, https://www.kijeka.com/wp-content/uploads/2017/11/Paper-Reel-Stacker-175x300.jpg 175w, https://www.kijeka.com/wp-content/uploads/2017/11/Paper-Reel-Stacker-768x1314.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/11/Paper-Reel-Stacker-599x1024.jpg 599w, https://www.kijeka.com/wp-content/uploads/2017/11/Paper-Reel-Stacker-53x90.jpg 53w, https://www.kijeka.com/wp-content/uploads/2017/11/Paper-Reel-Stacker-205x350.jpg 205w, https://www.kijeka.com/wp-content/uploads/2017/11/Paper-Reel-Stacker-281x480.jpg 281w, https://www.kijeka.com/wp-content/uploads/2017/11/Paper-Reel-Stacker-1170x2001.jpg 1170w, https://www.kijeka.com/wp-content/uploads/2017/11/Paper-Reel-Stacker-270x462.jpg 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Paper-Reel-Stacker-150x150.png",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Paper-Reel-Stacker-150x150.png 150w, https://www.kijeka.com/wp-content/uploads/2017/11/Paper-Reel-Stacker-170x170.png 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/semi-electric-stacker/",
                "name": "Semi Electric Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Semi-electric stacker is an economical choice for a variety of basic material handling needs ,which is a half electric forklift for load and unload and short- distance transportation.</li>\n<li>Cost effective handling solution for Vehicle Loading/Production Areas with minimum investment, energy saving &amp; regenerative safe &amp; efficient</li>\n<li><strong>The Battery Operated Pump is mounted directly on the hydraulic tank</strong></li>\n<li>The Lifting &amp; Lowering functions are controlled by a valve with built in Over pressure function, which prevents overload</li>\n<li>A lowering Brake valve ensures that the maximum lowering speed is not exceeded at full load</li>\n<li>Precise lifting &amp; Lowering via Hand Lever</li>\n<li>Design puts the focus on the safety &amp; ergonomic working condition of the user.</li>\n<li>Simple &amp; Convenient operation system</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Semi Electric Stacker </strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Load Center</td>\n<td width=\"324\">500mm</td>\n</tr>\n<tr>\n<td width=\"198\">Available\u00a0 Capacity</td>\n<td width=\"324\">1000Kgs, 1500Kgs, 2000Kgs.</td>\n</tr>\n<tr>\n<td width=\"198\">Available Lifting Height</td>\n<td width=\"324\">1600 mm,\u00a0 2000mm, 2500mm,3000mm, 3300mm\n<p>3500 mm, 4000mm</p></td>\n</tr>\n<tr>\n<td width=\"198\">Fork Length</td>\n<td width=\"324\">1150 mm</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Lower Height</td>\n<td width=\"324\">90mm</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Width</td>\n<td width=\"324\">550/600/ 360-680 mm (Adjustable Fork)</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Structure Design </strong></td>\n<td width=\"324\"><strong>Single Mast / Double Mast </strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Charging Voltage</strong></td>\n<td width=\"324\"><strong>AC 220V</strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Motor Power</strong></td>\n<td width=\"324\"><strong>1.6KW</strong></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Semi-Electric-Stacker.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Semi-Electric-Stacker.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/11/Semi-Electric-Stacker-198x300.jpg 198w, https://www.kijeka.com/wp-content/uploads/2017/11/Semi-Electric-Stacker-768x1165.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/11/Semi-Electric-Stacker-675x1024.jpg 675w, https://www.kijeka.com/wp-content/uploads/2017/11/Semi-Electric-Stacker-59x90.jpg 59w, https://www.kijeka.com/wp-content/uploads/2017/11/Semi-Electric-Stacker-231x350.jpg 231w, https://www.kijeka.com/wp-content/uploads/2017/11/Semi-Electric-Stacker-316x480.jpg 316w, https://www.kijeka.com/wp-content/uploads/2017/11/Semi-Electric-Stacker-270x410.jpg 270w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/semi-powered-drum-stacker/",
                "name": "Semi Powered Drum Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Battery Operated Drum Stacker is designed to raise and place a drum at required Location.</li>\n<li>Available to carry the drum to stack lower than 1600 mm.</li>\n<li>Eagle-grip design provide safest griping on Steel/HDPE Plastic Drums.</li>\n<li>Loading Capacity: 500 Kgs.</li>\n<li>Operating Type: Manual Propel , Eagle-grip Drum Holding,\u00a0 Battery OperatedUp-Down.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Transporting and Stacking of Drums.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td><strong>Semi Powered Drum Stacker</strong></td>\n</tr>\n<tr>\n<td>Operating Type</td>\n<td>/</td>\n<td>Manual Propel/Battery Operated Up-Down</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>500</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>1600 from Drum Bottom</td>\n</tr>\n<tr>\n<td>Total height</td>\n<td>mm</td>\n<td>2080</td>\n</tr>\n<tr>\n<td>Total length</td>\n<td>mm</td>\n<td>1230</td>\n</tr>\n<tr>\n<td>Total width</td>\n<td>mm</td>\n<td>850</td>\n</tr>\n<tr>\n<td>Inner/Outer Width of Front Leg</td>\n<td>mm</td>\n<td>630/1140</td>\n</tr>\n<tr>\n<td>Turning radius</td>\n<td>mm</td>\n<td>1430</td>\n</tr>\n<tr>\n<td>wheel size</td>\n<td>mm</td>\n<td>\u00d880*60/ \u00d8150*50</td>\n</tr>\n<tr>\n<td>Battery</td>\n<td>Ah/V</td>\n<td>120 Ah 12V</td>\n</tr>\n</tbody>\n</table>\n<p>\u00a0</p>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Stacker1.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Stacker1.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Stacker1-204x300.jpg 204w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Stacker1-768x1127.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Stacker1-698x1024.jpg 698w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Stacker1-61x90.jpg 61w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Stacker1-238x350.jpg 238w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Stacker1-327x480.jpg 327w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Stacker1-270x396.jpg 270w"
                    ],
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Stacker2-150x150.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Stacker2-150x150.jpg 150w, https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Stacker2-170x170.jpg 170w"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/semi-powered-drum-stacker-v-shaped-base/",
                "name": "Semi Powered Drum Stacker (V-Shaped Base)",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>The V-shaped base Drum Stacker is designed,so you can raise and place a drum at the corners of a pallet.</li>\n<li>Allow you to move drums on and off shipping pallets with help of\u00a0 Drum Stacker.</li>\n<li>Available to carry the drum to stack lower than 1100 mm.</li>\n<li>Eagle-grip design provide safest griping on Steel/HDPE Plastic Drums.</li>\n<li>Loading Capacity: 300 Kgs.</li>\n<li>Operating Type: Manual Propel , Eagle-grip\u00a0 Drum Holding, Battery OperatedUp-Down.</li>\n</ul>\n<p>\u00a0</p>\n<p><strong>Application:</strong></p>\n<ul>\n<li>Lifting, Transporting, Stacking, Palletizing of Drums.</li>\n<li>Frequent loading and unloading of Drums.</li>\n</ul>\n<p>\u00a0</p>\n<table>\n<tbody>\n<tr>\n<td colspan=\"2\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td><strong>Semi Powered Drum Stacker (V-Shaped Base)</strong></td>\n</tr>\n<tr>\n<td>Operating Type</td>\n<td>/</td>\n<td>Manual Propel/Battery Operated Up-Down</td>\n</tr>\n<tr>\n<td>Load capacity</td>\n<td>kg</td>\n<td>300</td>\n</tr>\n<tr>\n<td>Lifting height</td>\n<td>mm</td>\n<td>1100 from Drum Bottom</td>\n</tr>\n<tr>\n<td>Total height</td>\n<td>mm</td>\n<td>1870</td>\n</tr>\n<tr>\n<td>Total length</td>\n<td>mm</td>\n<td>1500</td>\n</tr>\n<tr>\n<td>Total width</td>\n<td>mm</td>\n<td>1350</td>\n</tr>\n<tr>\n<td>Turning radius</td>\n<td>mm</td>\n<td>1230</td>\n</tr>\n<tr>\n<td>wheel size</td>\n<td>mm</td>\n<td>\u00d8150*50, \u00d8125*50</td>\n</tr>\n<tr>\n<td>Battery</td>\n<td>Ah/V</td>\n<td>100 Ah 12V</td>\n</tr>\n<tr>\n<td>Net weight</td>\n<td>kg</td>\n<td>178</td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/06/Semi-Powered-Drum-Stacker-V-Shaped-Base.png"
                    ]
                ]
            },
            {
                "link": "https://www.kijeka.com/product/straddle-leg-manual-stacker/",
                "name": "Straddle Leg Manual Stacker",
                "desc": "<div class=\"woocommerce-product-details__short-description\">\n<ul>\n<li>Specially designed straddle legs allow the stacker to be used to enter special size cargos where base legs could interfere, and at the same time improve the stability.</li>\n</ul>\n<p>\u00a0</p>\n<table width=\"522\">\n<tbody>\n<tr>\n<td width=\"198\">\n<p style=\"text-align: center;\"><strong>Model</strong></p>\n</td>\n<td width=\"324\"><strong>Straddle Leg Manual Stacker</strong></td>\n</tr>\n<tr>\n<td width=\"198\">MOC</td>\n<td width=\"324\">MS Powder Coated Finish Or Paint</td>\n</tr>\n<tr>\n<td width=\"198\">Drive Type</td>\n<td width=\"324\">Manual Push-Pull Type, Hydraulic Up-Down</td>\n</tr>\n<tr>\n<td width=\"198\">Standard Capacity</td>\n<td width=\"324\">1000 kgs</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Length</td>\n<td width=\"324\">1150 mm</td>\n</tr>\n<tr>\n<td width=\"198\">Fork Width</td>\n<td width=\"324\">300-850 mm (Adjustable Fork)</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Structure Design </strong></td>\n<td width=\"324\"><strong>Single Mast / Double Mast </strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Lifting Height</strong></td>\n<td width=\"324\"><strong>1600mm Standard, 2000mm, 2500mm, 3000mm</strong></td>\n</tr>\n<tr>\n<td width=\"198\">Structure Design</td>\n<td width=\"324\">Single Mast / Double Mast</td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Available Capacities </strong></td>\n<td width=\"324\"><strong>1000 kgs, 1500 Kgs </strong></td>\n</tr>\n<tr>\n<td width=\"198\"><strong>Available Drive Option</strong></td>\n<td width=\"324\"><strong>Manual-Hydraulic, Electric Operated, </strong>\n<p><strong>Battery Operated Up-Down</strong></p></td>\n</tr>\n</tbody>\n</table>\n</div>",
                "images": [
                    [
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Straddle-Base-Stacker.jpg",
                        "https://www.kijeka.com/wp-content/uploads/2017/11/Straddle-Base-Stacker.jpg 1000w, https://www.kijeka.com/wp-content/uploads/2017/11/Straddle-Base-Stacker-227x300.jpg 227w, https://www.kijeka.com/wp-content/uploads/2017/11/Straddle-Base-Stacker-768x1015.jpg 768w, https://www.kijeka.com/wp-content/uploads/2017/11/Straddle-Base-Stacker-775x1024.jpg 775w, https://www.kijeka.com/wp-content/uploads/2017/11/Straddle-Base-Stacker-68x90.jpg 68w, https://www.kijeka.com/wp-content/uploads/2017/11/Straddle-Base-Stacker-265x350.jpg 265w, https://www.kijeka.com/wp-content/uploads/2017/11/Straddle-Base-Stacker-363x480.jpg 363w, https://www.kijeka.com/wp-content/uploads/2017/11/Straddle-Base-Stacker-270x357.jpg 270w"
                    ]
                ]
            }
        ],
        "Plastic Pallet": []
    }
    for key,item in data.items():
        for i in item:
            imageArr = []
            for image in i['images']:
                imageArr.append(image[0])
            print("./media/images/"+imageArr[0].split("/")[-1])
            newProduct = Product()
            newProduct.productName = i['name']
            newProduct.category = Category.objects.filter(categoryName=key).first()
            newProduct.description = "<!DOCTYPE html><html><head><title></title></head><body>"+i['desc']+"</body></html>"
            newProduct.images = "./media/images/"+imageArr[0].split("/")[-1]
            newProduct.isUploaded = True
            newProduct.save()
    return HttpResponse(json.dumps({'msg': 'Category added successfully.'}), content_type='application/json')

@csrf_exempt
def dataUpdater(request):
    products = Product.objects.all()
    for product in products:
        #product.description = product.description.replace("rgb(0, 75, 149)","rgb(0, 75, 149)")
        # product.description = product.description.split("<h1")[0] + product.description.split("<h1")[1].split("</h1>")[1]
        old = product.productName
        product.productName = (product.productName).replace("  "," ")
        if old != product.productName:
            product.save()
    return HttpResponse(json.dumps({'msg': 'Category updated successfully.'}), content_type='application/json')

@csrf_exempt
def quotesAdder(request):
    data = ["Drum pumps are an essential tool for the safe and efficient transfer of fluids from drums and other containers.","Drum pumps are the go-to solution for handling viscous or corrosive liquids in industrial and chemical applications.","Drum pumps are a versatile and cost-effective solution for transferring a wide range of fluids, from light oils to harsh chemicals.","Drum pumps can significantly improve the safety and efficiency of fluid transfer operations by reducing spills, leaks, and worker exposure to hazardous materials.","Drum pumps are available in a variety of materials, sizes, and styles to meet the specific needs of any application.","The right drum pump can make all the difference in the safe and efficient handling of chemicals, oils, and other fluids in manufacturing and processing operations.","Drum pumps are an essential component of any industrial fluid transfer operation, enabling workers to move fluids from drums and other containers with ease and precision.","By using a drum pump, workers can minimize the risk of spills, leaks, and accidents during fluid transfer, ensuring a safer and more efficient work environment.","Drum pumps are a critical part of any industrial or manufacturing process that involves the transfer of liquids or chemicals. The right pump can improve safety, reduce waste, and increase productivity.","Drum pumps are an economical and efficient solution for transferring a wide range of fluids, offering a fast and easy way to move liquids from drums, tanks, and other containers."]
    for i in data:
        newQuote = Quote()
        newQuote.quote = i
        newQuote.category = Category.objects.filter(categoryName="Oil Pumps, Meters & Acces.").first()
        newQuote.save()
    return HttpResponse(json.dumps({'msg': 'data added successfully.'}), content_type='application/json')


