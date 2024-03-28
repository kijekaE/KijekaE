from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from api.models import Blog
from django.http import FileResponse


@csrf_exempt
def blogDynamic(request,link):
    print(link)
    blog  = Blog.objects.filter(blogLink=link).first()
    blog.views = blog.views + 1
    blog.save()
    return render(request, 'index.html')
@csrf_exempt
def pdfCatalog(request):
    return redirect('/static/Kijeka_Catalogue.pdf')
   


@csrf_exempt
@login_required(login_url='/dashboard/login/')
def dashboard(request):
    return render(request, 'admin.html')

@csrf_exempt
def loginPage(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def youtubevideos(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def review(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def addProducts(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def hotProducts(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def allProducts(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def clientLogos(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def blog(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def newBlog(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def draftsBlog(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def reviewBlog(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def approvedBlog(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def publishedBlog(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def rejectedBlog(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def deleteBlog(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def imageSlider(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def contactdetails(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def reachusform(request):
    return render(request, 'admin.html')

@login_required(login_url='/dashboard/login/')
def careers(request):
    return render(request, 'admin.html')

