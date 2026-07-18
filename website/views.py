from django.shortcuts import render
from django.http import HttpResponse
from .models import Product

def home(request):
    products = Product.objects.filter(
        available=True,
        featured=True
    )

    return render(request, "home.html", {
        "products": products
    })

def about(request):
    return render(request, "about.html")

def menu(request):
    return render(request, "menu.html")

def contact(request):
    return render(request, "contact.html")
# Create your views here.
