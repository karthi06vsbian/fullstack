import json
from decimal import Decimal
from urllib.parse import quote

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .integrations import create_razorpay_order, create_shiprocket_order, verify_razorpay_signature
from .models import Order, OrderItem, Product
from .shipping import calculate_shipping


def body_json(request):
    try:
        return json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return {}


def admin_allowed(request):
    password = request.headers.get("X-Admin-Password") or request.GET.get("password")
    return password and password == settings.ADMIN_PANEL_PASSWORD


def require_admin(request):
    if not admin_allowed(request):
        return JsonResponse({"error": "Admin password is required."}, status=401)
    return None


def product_json(product):
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "category": product.category,
        "description": product.description,
        "material": product.material,
        "price": float(product.price),
        "rating": float(product.rating),
        "image": f"/media/{product.image}",
        "stock": product.stock,
        "weight_grams": product.weight_grams,
        "is_featured": product.is_featured,
        "is_custom": product.is_custom,
    }


def unique_product_slug(name):
    slug = slugify(name)[:180] or "product"
    original = slug
    counter = 2
    while Product.objects.filter(slug=slug).exists():
        slug = f"{original}-{counter}"[:200]
        counter += 1
    return slug


def product_image_path(image):
    clean = str(image or "").strip()
    for prefix in ("/productsimg/", "productsimg/", "/media/", "media/"):
        if clean.startswith(prefix):
            return clean[len(prefix):]
    return clean or "none"


def order_item_price(item):
    try:
        price = Decimal(str(item.get("price") or 0))
    except Exception:
        price = Decimal("0")
    return max(Decimal("0"), price)


def apply_order_item_snapshot(product, item):
    product.name = str(item.get("name") or product.name).strip()[:180] or product.name
    product.price = order_item_price(item)
    product.category = str(item.get("category") or product.category).strip()[:80] or product.category
    product.description = str(item.get("description") or product.description)
    product.material = str(item.get("material") or product.material).strip()[:80] or product.material
    try:
        product.rating = Decimal(str(item.get("rating") or product.rating))
        product.stock = max(product.stock, int(item.get("stock") or product.stock))
        product.weight_grams = max(1, int(item.get("weight_grams") or product.weight_grams))
    except Exception:
        pass
    product.is_featured = bool(item.get("is_featured", product.is_featured))
    product.is_custom = bool(item.get("is_custom", product.is_custom))
    product.save(update_fields=["name", "price", "category", "description", "material", "rating", "stock", "weight_grams", "is_featured", "is_custom"])
    return product


def create_product_from_snapshot(item):
    name = str(item.get("name") or "Custom 3D Print").strip()[:180]
    return Product.objects.create(
        name=name,
        slug=unique_product_slug(name),
        category=str(item.get("category") or "Products").strip()[:80],
        description=str(item.get("description") or "3D printed product ready for order or customization."),
        material=str(item.get("material") or "PLA").strip()[:80],
        price=order_item_price(item),
        rating=Decimal(str(item.get("rating") or 4.8)),
        image=product_image_path(item.get("image")),
        stock=max(20, int(item.get("stock") or 20)),
        weight_grams=max(1, int(item.get("weight_grams") or 250)),
        is_featured=bool(item.get("is_featured", False)),
        is_custom=bool(item.get("is_custom", False)),
    )


def product_from_order_item(item):
    product_id = item.get("product_id")
    try:
        if product_id:
            return Product.objects.get(id=int(product_id))
    except (Product.DoesNotExist, TypeError, ValueError):
        pass

    image = product_image_path(item.get("image"))
    existing = Product.objects.filter(image=image).first()
    if existing:
        return apply_order_item_snapshot(existing, item)

    return create_product_from_snapshot(item)


def order_json(order):
    return {
        "id": order.id,
        "order_number": f"PF-{order.id}",
        "customer_name": order.customer_name,
        "phone": order.phone,
        "email": order.email,
        "address_line": order.address_line,
        "city": order.city,
        "state": order.state,
        "pincode": order.pincode,
        "subtotal": float(order.subtotal),
        "shipping_charge": float(order.shipping_charge),
        "total": float(order.total),
        "status": order.status,
        "payment_method": order.payment_method,
        "razorpay_order_id": order.razorpay_order_id,
        "shipment_id": order.shipment_id,
        "tracking_url": order.tracking_url,
        "items": [
            {
                "product_id": item.product_id,
                "name": item.product_name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "custom_note": item.custom_note,
            }
            for item in order.items.all()
        ],
    }


@require_GET
def health(_request):
    return JsonResponse({"status": "ok", "app": "XTRUDE 3D API"})


@require_GET
def products(request):
    queryset = Product.objects.all()
    category = request.GET.get("category")
    search = request.GET.get("search")
    featured = request.GET.get("featured")
    if category:
        queryset = queryset.filter(category__iexact=category)
    if search:
        queryset = queryset.filter(name__icontains=search)
    if featured == "1":
        queryset = queryset.filter(is_featured=True)
    categories = list(Product.objects.values_list("category", flat=True).distinct().order_by("category"))
    return JsonResponse({"products": [product_json(product) for product in queryset], "categories": categories})


@require_GET
def product_detail(_request, slug):
    return JsonResponse({"product": product_json(get_object_or_404(Product, slug=slug))})


@csrf_exempt
@require_POST
def shipping_quote(request):
    data = body_json(request)
    try:
        quote_data = calculate_shipping(
            data.get("pincode", ""),
            total_weight_grams=data.get("weight_grams", 250),
            subtotal=data.get("subtotal", 0),
            payment_method=data.get("payment_method", "razorpay"),
        )
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse(quote_data)


@csrf_exempt
@require_POST
@transaction.atomic
def create_order(request):
    data = body_json(request)
    items = data.get("items", [])
    if not items:
        return JsonResponse({"error": "Cart is empty."}, status=400)

    subtotal = Decimal("0.00")
    weight = 0
    order_items = []
    for item in items:
        product = product_from_order_item(item)
        quantity = max(1, int(item.get("quantity", 1)))
        if quantity > product.stock:
            return JsonResponse({"error": f"Only {product.stock} available for {product.name}."}, status=400)
        subtotal += product.price * quantity
        weight += product.weight_grams * quantity
        order_items.append((product, quantity, item.get("custom_note", "")))

    customer = data.get("customer", {})
    required = ["name", "email", "phone", "address_line", "city", "state", "pincode"]
    missing = [key for key in required if not customer.get(key)]
    if missing:
        return JsonResponse({"error": f"Missing customer fields: {', '.join(missing)}"}, status=400)

    try:
        payment_method = data.get("payment_method", "razorpay")
        if payment_method not in {"razorpay", "cod"}:
            return JsonResponse({"error": "Choose Razorpay or Cash on Delivery."}, status=400)
        shipping = calculate_shipping(customer["pincode"], weight, subtotal, payment_method)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    shipping_charge = Decimal(str(shipping["total_delivery_charge"]))
    total = subtotal + shipping_charge
    order = Order.objects.create(
        customer_name=customer["name"],
        email=customer["email"],
        phone=customer["phone"],
        address_line=customer["address_line"],
        city=customer["city"],
        state=customer["state"],
        pincode=customer["pincode"],
        subtotal=subtotal,
        shipping_charge=shipping_charge,
        total=total,
        payment_method=payment_method,
    )

    for product, quantity, custom_note in order_items:
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            quantity=quantity,
            unit_price=product.price,
            custom_note=custom_note,
        )

    razorpay_payload = {"key": settings.RAZORPAY_KEY_ID, "order_id": "", "amount": int(order.total * 100), "currency": "INR"}
    if payment_method == "razorpay":
        try:
            razorpay_order = create_razorpay_order(order)
        except Exception as exc:
            transaction.set_rollback(True)
            return JsonResponse({
                "error": f"Razorpay order could not be created: {exc}. Check RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in Render, then restart the backend."
            }, status=502)
        order.razorpay_order_id = razorpay_order["id"]
        order.save(update_fields=["razorpay_order_id"])
        razorpay_payload["order_id"] = order.razorpay_order_id
    else:
        order.status = "processing"
        shipment = create_shiprocket_order(order)
        order.shiprocket_order_id = shipment.get("shiprocket_order_id", "")
        order.shipment_id = shipment.get("shipment_id", "")
        order.tracking_url = shipment.get("tracking_url", "")
        order.save()

    return JsonResponse({
        "order": order_json(order),
        "shipping": shipping,
        "razorpay": razorpay_payload,
    }, status=201)


@require_GET
def order_detail(_request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), id=order_id)
    return JsonResponse({"order": order_json(order)})


@csrf_exempt
@require_POST
@transaction.atomic
def verify_payment(request):
    data = body_json(request)
    order = get_object_or_404(Order, id=data.get("order_id"))
    if not verify_razorpay_signature(
        data.get("razorpay_order_id", order.razorpay_order_id),
        data.get("razorpay_payment_id", ""),
        data.get("razorpay_signature", ""),
    ):
        return JsonResponse({"error": "Payment verification failed."}, status=400)

    order.status = "paid"
    order.razorpay_payment_id = data.get("razorpay_payment_id", "")
    shipment = create_shiprocket_order(order)
    order.shiprocket_order_id = shipment.get("shiprocket_order_id", "")
    order.shipment_id = shipment.get("shipment_id", "")
    order.tracking_url = shipment.get("tracking_url", "")
    order.save()
    return JsonResponse({"order": order_json(order), "shipment": shipment})


@require_GET
def whatsapp_link(request):
    message = request.GET.get(
        "message",
        "Hi XTRUDE, I need help with a 3D printed product order.",
    )
    return JsonResponse({"url": f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={quote(message)}"})


@require_GET
def admin_summary(_request):
    denied = require_admin(_request)
    if denied:
        return denied
    order_totals = Order.objects.aggregate(total_revenue=Sum("total"), total_orders=Count("id"))
    status_counts = list(Order.objects.values("status").annotate(count=Count("id")).order_by("status"))
    category_counts = list(Product.objects.values("category").annotate(count=Count("id")).order_by("category"))
    return JsonResponse({
        "stats": {
            "orders": order_totals["total_orders"] or 0,
            "revenue": float(order_totals["total_revenue"] or 0),
            "products": Product.objects.count(),
            "cod_orders": Order.objects.filter(payment_method="cod").count(),
            "razorpay_orders": Order.objects.filter(payment_method="razorpay").count(),
        },
        "status_counts": status_counts,
        "category_counts": category_counts,
        "recent_orders": [order_json(order) for order in Order.objects.prefetch_related("items")[:8]],
        "products": [product_json(product) for product in Product.objects.all()],
    })


@require_GET
def admin_orders(_request):
    denied = require_admin(_request)
    if denied:
        return denied
    orders = Order.objects.prefetch_related("items").all()[:50]
    return JsonResponse({"orders": [order_json(order) for order in orders]})


@csrf_exempt
@require_POST
def admin_login(request):
    denied = require_admin(request)
    if denied:
        return denied
    return JsonResponse({"ok": True})


@csrf_exempt
@require_POST
def admin_update_product(request, product_id):
    denied = require_admin(request)
    if denied:
        return denied
    data = body_json(request)
    product = get_object_or_404(Product, id=product_id)
    if "name" in data:
        product.name = str(data["name"]).strip()[:180] or product.name
    if "price" in data:
        try:
            product.price = Decimal(str(data["price"]))
        except Exception:
            return JsonResponse({"error": "Enter a valid price."}, status=400)
    product.save(update_fields=["name", "price"])
    return JsonResponse({"product": product_json(product)})


@csrf_exempt
@require_POST
def admin_sync_product(request):
    denied = require_admin(request)
    if denied:
        return denied
    data = body_json(request)
    image = product_image_path(data.get("image"))
    product = Product.objects.filter(image=image).first()
    if product:
        product = apply_order_item_snapshot(product, data)
    else:
        product = create_product_from_snapshot(data)
    return JsonResponse({"product": product_json(product)}, status=201)
