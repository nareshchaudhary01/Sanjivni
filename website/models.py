from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):

    CATEGORY_CHOICES = [
    ("Powder", "Powder"),
    ("Tea", "Tea"),
    ("Capsules", "Capsules"),
    ("Oil", "Oil"),
    ]

    name = models.CharField(max_length=100)

    category = models.CharField(
    max_length=20,
    choices=CATEGORY_CHOICES,
    default="Powder"
    )

    slug = models.SlugField(unique=True)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to="products/"
    )

    featured = models.BooleanField(default=False)

    available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class ContactMessage(models.Model):

    name = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(max_length=15)

    subject = models.CharField(max_length=200)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cart(models.Model):

    session_key = models.CharField(
        max_length=100,
        unique=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.session_key

    def get_total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())


class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):


    user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    null=True,
    blank=True
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()


    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('ONLINE', 'Online Payment (Pay Now)'),
    ]

    payment_method = models.CharField(
        max_length=10, 
        choices=PAYMENT_CHOICES, 
        default='COD'
    )

    STATUS_CHOICES = [
    ("Pending", "Pending"),
    ("Processing", "Processing"),
    ("Shipped", "Shipped"),
    ("Delivered", "Delivered"),
    ("Cancelled", "Cancelled"),
    ]
    
    total = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(max_digits=10, decimal_places=2)


    @property
    def subtotal(self):
        return self.price * self.quantity

    @property
    def can_cancel(self):
        return self.status in ["Pending", "Processing"]

    def __str__(self):
        return self.product.name
    
# Create your models here.
