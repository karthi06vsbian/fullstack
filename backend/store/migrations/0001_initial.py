from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("slug", models.SlugField(max_length=200, unique=True)),
                ("category", models.CharField(max_length=80)),
                ("description", models.TextField(blank=True)),
                ("material", models.CharField(default="PLA", max_length=80)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("rating", models.DecimalField(decimal_places=1, default=4.8, max_digits=3)),
                ("image", models.CharField(max_length=255)),
                ("stock", models.PositiveIntegerField(default=25)),
                ("weight_grams", models.PositiveIntegerField(default=250)),
                ("is_featured", models.BooleanField(default=False)),
                ("is_custom", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["category", "name"]},
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_name", models.CharField(max_length=160)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=20)),
                ("address_line", models.TextField()),
                ("city", models.CharField(max_length=100)),
                ("state", models.CharField(max_length=100)),
                ("pincode", models.CharField(max_length=10)),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=10)),
                ("shipping_charge", models.DecimalField(decimal_places=2, max_digits=10)),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                ("payment_method", models.CharField(choices=[("razorpay", "Razorpay"), ("cod", "Cash on Delivery")], default="razorpay", max_length=20)),
                ("status", models.CharField(choices=[("pending_payment", "Pending Payment"), ("paid", "Paid"), ("processing", "Processing"), ("shipped", "Shipped"), ("delivered", "Delivered"), ("cancelled", "Cancelled")], default="pending_payment", max_length=24)),
                ("razorpay_order_id", models.CharField(blank=True, max_length=120)),
                ("razorpay_payment_id", models.CharField(blank=True, max_length=120)),
                ("shiprocket_order_id", models.CharField(blank=True, max_length=120)),
                ("shipment_id", models.CharField(blank=True, max_length=120)),
                ("tracking_url", models.URLField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_name", models.CharField(max_length=180)),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("custom_note", models.TextField(blank=True)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="store.order")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="store.product")),
            ],
        ),
    ]
