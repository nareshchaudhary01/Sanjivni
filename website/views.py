from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Product, ContactMessage, Cart, CartItem
from .forms import CheckoutForm
from .models import Order, OrderItem




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

    query = request.GET.get("q")

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    return render(request, "menu.html", {
        "products": products,
        "query": query,
    })

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


def get_cart(request):
    session_key = request.session.session_key

    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(
        id=request.session.get("cart_id")
    ) if request.session.get("cart_id") else (None, True)

    if cart is None:
        cart = Cart.objects.create()
        request.session["cart_id"] = cart.id

    return cart


def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)

    cart = get_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")

def cart(request):
    cart = get_cart(request)

    items = CartItem.objects.filter(cart=cart)

    total = sum(item.total_price for item in items)

    return render(request, "cart.html", {
        "items": items,
        "total": total
    })


def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.quantity += 1
    item.save()
    return redirect("cart")


def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect("cart")


def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect("cart")

def checkout(request):

    cart = get_cart(request)

    items = cart.items.all()

    total = sum(item.total_price for item in items)

    if request.method == "POST":

        form = CheckoutForm(request.POST)

        if form.is_valid():

            order = form.save(commit=False)

            order.total = total

            order.save()

            for item in items:

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                )

            items.delete()

            return redirect("thank_you")

    else:

        form = CheckoutForm()

    return render(request, "checkout.html", {
        "form": form,
        "items": items,
        "total": total,
    })

def thank_you(request):
    return render(request, "thank_you.html")
# Create your views here.
