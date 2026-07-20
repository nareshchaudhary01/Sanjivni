from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Product, ContactMessage, Cart, CartItem
from .forms import CheckoutForm
from .models import Order, OrderItem
from django.contrib.auth import login
from .forms import SignupForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings



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
    category = request.GET.get("category")

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category:
        products = products.filter(category=category)

    return render(request, "menu.html", {
        "products": products,
        "query": query,
        "category": category,
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

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(
        session_key=session_key
    )

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

            # Logged in user ko order se link karo
            if request.user.is_authenticated:
                order.user = request.user

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

def signup(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect("home")

    else:

        form = SignupForm()

    return render(
        request,
        "signup.html",
        {
            "form": form
        }
    )

def user_logout(request):
    logout(request)
    return redirect("home")

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "my_orders.html",
        {
            "orders": orders
        }
    )


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ["Pending", "Processing"]:
        order.status = "Cancelled"
        order.save()
        
        # EMAIL BHEJNE KA CODE
        try:
            send_mail(
                subject=f'Alert: Order #{order.id} Cancelled!',
                message=f'User {order.name} has cancelled Order #{order.id}. Total amount: {order.total}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['apka_email@gmail.com'], # Yahan apna email dalo
                fail_silently=True,
        )
        except Exception:
            pass

        messages.success(request, f"Order #{order.id} has been cancelled successfully.")
    else:
        messages.error(request, "Cannot cancel this order.")

    return redirect('my_orders')
# Create your views here.
