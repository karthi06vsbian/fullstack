from django.contrib import admin

from .models import Order, OrderItem, Product


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "unit_price")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_featured", "is_custom")
    list_filter = ("category", "is_featured", "is_custom")
    search_fields = ("name", "category", "material")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "phone", "pincode", "total", "status", "created_at")
    list_filter = ("status", "payment_method", "state")
    search_fields = ("customer_name", "email", "phone", "pincode", "razorpay_order_id", "shipment_id")
    inlines = [OrderItemInline]
