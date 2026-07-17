from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, "home.html")

def about(request):
    return render(request, "about.html")

def menu(request):
    return render(request, "menu.html")

def contact(request):
    return render(request, "contact.html")
# Create your views here.
