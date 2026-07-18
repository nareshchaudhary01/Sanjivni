from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Product, ContactMessage




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

    if request.method == "POST":

        ContactMessage.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            subject=request.POST.get("subject"),
            message=request.POST.get("message"),
        )

        return redirect("contact")

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
