from decimal import Decimal

from django.conf import settings


PINCODE_ZONES = [
    ("641", "Coimbatore local", Decimal("45.00"), 1),
    ("642", "Coimbatore region", Decimal("55.00"), 1),
    ("643", "Nilgiris / nearby", Decimal("75.00"), 2),
    ("6", "South India", Decimal("95.00"), 3),
    ("5", "South India", Decimal("110.00"), 4),
    ("4", "West India", Decimal("135.00"), 5),
    ("3", "West / North India", Decimal("145.00"), 6),
    ("2", "North India", Decimal("155.00"), 7),
    ("1", "North India", Decimal("165.00"), 7),
    ("7", "East India", Decimal("175.00"), 8),
    ("8", "East India", Decimal("185.00"), 8),
]


def calculate_shipping(pincode, total_weight_grams=250, subtotal=0, payment_method="razorpay"):
    clean = "".join(ch for ch in str(pincode) if ch.isdigit())
    if len(clean) != 6:
        raise ValueError("Enter a valid 6 digit Indian pincode.")

    zone_name = "Remote India"
    base = Decimal("210.00")
    delivery_days = 9
    for prefix, name, charge, days in PINCODE_ZONES:
        if clean.startswith(prefix):
            zone_name = name
            base = charge
            delivery_days = days
            break

    weight = Decimal(max(int(total_weight_grams or 250), 250))
    extra_blocks = max(Decimal("0"), (weight - Decimal("500")) / Decimal("500"))
    charge = base + (extra_blocks.to_integral_value(rounding="ROUND_CEILING") * Decimal("35.00"))
    subtotal = Decimal(str(subtotal or 0))
    if subtotal >= Decimal("2499.00"):
        charge = Decimal("0.00")
    cod_charge = Decimal("0.00")
    if payment_method == "cod":
        cod_charge = max(Decimal("45.00"), (subtotal * Decimal("0.02")).quantize(Decimal("1.00")))

    return {
        "hub": settings.HUB_CITY,
        "hub_pincode": settings.HUB_PINCODE,
        "destination_pincode": clean,
        "zone": zone_name,
        "shipping_charge": float(charge),
        "cod_charge": float(cod_charge),
        "total_delivery_charge": float(charge + cod_charge),
        "estimated_days": delivery_days,
        "service": "Shiprocket Express COD" if payment_method == "cod" else "Shiprocket Express",
        "free_shipping_applied": charge == 0,
    }
