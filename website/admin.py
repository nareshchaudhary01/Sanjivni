from django.contrib import admin
from .models import Product, ContactMessage, Cart, CartItem, Order, OrderItem

# 1. Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "featured",
        "available",
    )
    list_filter = (
        "featured",
        "available",
    )
    search_fields = (
        "name",
    )
    prepopulated_fields = {
        "slug": ("name",)
    }


# 2. Contact Message Admin
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
        "subject",
        "created_at",
    )
    search_fields = (
        "name",
        "email",
        "subject",
    )
    list_filter = (
        "created_at",
    )
    ordering = (
        "-created_at",
    )


# 3. Cart & CartItem Admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
    )
    ordering = (
        "-created_at",
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "cart",
        "product",
        "quantity",
        "total_price",
    )
    list_filter = (
        "cart",
    )
    search_fields = (
        "product__name",
    )


# 4. Order & OrderItem Admin
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')


admin.site.register(OrderItem)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Table list me payment_method aur custom badge dono dikhenge
    list_display = (
        'id', 
        'name', 
        'total', 
        'get_payment_method',  # COD / Online yahan dikhega
        'status', 
        'created_at'
    )
    list_filter = ('status', 'payment_method', 'created_at') # Filter me payment_method add kiya
    search_fields = ('name', 'email', 'id')
    inlines = [OrderItemInline] # Order ke andar hi purchased products dikhenge

    # Payment Method ko Admin me clean text/emoji me dikhane ke liye
    @admin.display(description='Payment Method')
    def get_payment_method(self, obj):
        if getattr(obj, 'payment_method', '') == 'ONLINE':
            return '💳 Online (Pay Now)'
        return '💵 Cash on Delivery (COD)'