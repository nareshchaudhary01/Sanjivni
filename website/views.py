from django.shortcuts import render,  get_object_or_404
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
    products = Product.objects.filter(available=True)

    context = {
        "products": products
    }

    return render(request, "menu.html", context)

def contact(request):
    return render(request, "contact.html")

def product_detail(request, slug):

    product = get_object_or_404(
        Product,
        slug=slug,
        available=True
    )

    return render(
        request,
        "product_detail.html",
        {
            "product": product
        }
    )
# Create your views here.
