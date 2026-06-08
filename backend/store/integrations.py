import hashlib
import hmac
from decimal import Decimal

import requests
from django.conf import settings


def create_razorpay_order(order):
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return {
            "id": f"dev_rzp_{order.id}",
            "amount": int(order.total * 100),
            "currency": "INR",
            "dev_mode": True,
        }

    import razorpay

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    return client.order.create({
        "amount": int(order.total * 100),
        "currency": "INR",
        "receipt": f"PF-{order.id}",
        "payment_capture": 1,
    })


def verify_razorpay_signature(order_id, payment_id, signature):
    if not settings.RAZORPAY_KEY_SECRET:
        return True

    message = f"{order_id}|{payment_id}".encode()
    digest = hmac.new(settings.RAZORPAY_KEY_SECRET.encode(), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature)


def create_shiprocket_order(order):
    if not settings.SHIPROCKET_EMAIL or not settings.SHIPROCKET_PASSWORD:
        return {
            "shiprocket_order_id": f"dev_sr_{order.id}",
            "shipment_id": f"dev_ship_{order.id}",
            "tracking_url": "",
            "dev_mode": True,
        }

    token_response = requests.post(
        "https://apiv2.shiprocket.in/v1/external/auth/login",
        json={"email": settings.SHIPROCKET_EMAIL, "password": settings.SHIPROCKET_PASSWORD},
        timeout=15,
    )
    token_response.raise_for_status()
    token = token_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    items = [
        {
            "name": item.product_name,
            "sku": f"PF-{item.product_id}",
            "units": item.quantity,
            "selling_price": str(item.unit_price),
        }
        for item in order.items.select_related("product")
    ]
    payload = {
        "order_id": f"PF-{order.id}",
        "order_date": order.created_at.strftime("%Y-%m-%d %H:%M"),
        "pickup_location": settings.HUB_CITY,
        "billing_customer_name": order.customer_name,
        "billing_address": order.address_line,
        "billing_city": order.city,
        "billing_pincode": order.pincode,
        "billing_state": order.state,
        "billing_country": "India",
        "billing_email": order.email,
        "billing_phone": order.phone,
        "shipping_is_billing": True,
        "order_items": items,
        "payment_method": "Prepaid" if order.payment_method == "razorpay" else "COD",
        "sub_total": str(order.subtotal),
        "length": 16,
        "breadth": 12,
        "height": 8,
        "weight": max(Decimal("0.2"), Decimal(sum(i.product.weight_grams * i.quantity for i in order.items.all())) / 1000),
    }
    response = requests.post(
        "https://apiv2.shiprocket.in/v1/external/orders/create/adhoc",
        json=payload,
        headers=headers,
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "shiprocket_order_id": str(data.get("order_id", "")),
        "shipment_id": str(data.get("shipment_id", "")),
        "tracking_url": "",
    }
