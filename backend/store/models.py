from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    material = models.CharField(max_length=80, default="PLA")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.8)
    image = models.CharField(max_length=255)
    stock = models.PositiveIntegerField(default=25)
    weight_grams = models.PositiveIntegerField(default=250)
    is_featured = models.BooleanField(default=False)
    is_custom = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending_payment", "Pending Payment"),
        ("paid", "Paid"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_CHOICES = [
        ("razorpay", "Razorpay"),
        ("cod", "Cash on Delivery"),
    ]

    customer_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="razorpay")
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default="pending_payment")
    razorpay_order_id = models.CharField(max_length=120, blank=True)
    razorpay_payment_id = models.CharField(max_length=120, blank=True)
    shiprocket_order_id = models.CharField(max_length=120, blank=True)
    shipment_id = models.CharField(max_length=120, blank=True)
    tracking_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"PF-{self.id or 'new'} {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=180)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    custom_note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
