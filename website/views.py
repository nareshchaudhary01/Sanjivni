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
import razorpay
from django.views.decorators.csrf import csrf_exempt



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
            phone=request.POST.get("phone"),
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

@login_required(login_url="login")
def checkout(request):
    # Cart ko session_key ya ID se fetch karo (User field cart me nahi hai)
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart = get_object_or_404(Cart, id=cart_id)
    else:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()

    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty!")
        return redirect('cart')

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        if not payment_method:
            messages.error(request, "Please select a payment method!")
            return redirect('checkout')

        # Order create karo
        order = Order.objects.create(
            user=request.user,
            name=name,
            email=email,
            phone=phone,
            address=address,
            total=cart.get_total_price(),
            payment_method=payment_method,
            status="Pending"
        )

        # Cart items ko Order items me copy karo
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
        
        # Cart khali karo
        cart.items.all().delete()

        # Payment Method Redirection Logic
        if payment_method == 'ONLINE':
            return redirect('payment_page', order_id=order.id)
        else:
            messages.success(request, f"Order #{order.id} placed successfully with Cash on Delivery!")
            return redirect('my_orders')

    return render(request, 'checkout.html', {'cart': cart})
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


# 1. Initiate Payment View
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Razorpay Client Init
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Amount in paise (e.g. ₹199 = 19900 paise)
    amount_in_paise = int(order.total * 100)
    
    # Create Razorpay Order
    razorpay_order = client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "payment_capture": "1"
    })
    
    context = {
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': order.total,
        'amount_in_paise': amount_in_paise,
    }
    return render(request, 'payment.html', context)

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')
        order_id = request.POST.get('order_id', '')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            # Verify payment signature
            client.utility.verify_payment_signature(params_dict)
            
            # Update order status to Processing/Paid
            order = Order.objects.get(id=order_id)
            order.status = "Processing"
            order.save()

            messages.success(request, f"Payment successful! Order #{order.id} is now being processed.")
            return redirect('thank_you')

        except Exception as e:
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect('my_orders')

    return redirect('my_orders')

# Create your views here.
