from pathlib import Path
from random import Random

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from store.models import Product


CATEGORY_LABELS = {
    "home-decor": "Home Decor",
    "keychains": "Keychains",
    "custom-names": "Custom Names",
    "organizer": "Organizer",
    "pets": "Pets",
    "projects": "Projects",
    "toys": "Toys",
    "useful-appliances": "Organizer",
}

CATEGORY_PRICE_RANGES = {
    "Home Decor": (349, 1299),
    "Keychains": (129, 449),
    "Custom Names": (149, 699),
    "Organizer": (199, 1399),
    "Pets": (199, 799),
    "Projects": (699, 2499),
    "Toys": (199, 999),
}

MATERIALS = ["PLA", "Matte PLA", "Silk PLA", "PETG"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

PRODUCT_NAMES = {
    "organizer/organizer-01.png": "Daily Reminder Tracker 7 Day Slider",
    "organizer/organizer-02.png": "Small Storage Box",
    "organizer/organizer-03.png": "Storage Box",
    "organizer/organizer-04.png": "Key Hanger",
    "organizer/organizer-05.png": "Home Key Hanger",
    "organizer/organizer-06.png": "Organizer Box",
    "organizer/organizer-07.png": "Lid Organizer",
    "organizer/organizer-08.png": "Desktop Organizer",
    "organizer/organizer-09.png": "Ferrari Desktop Organizer",
    "organizer/organizer-10.png": "Desk Tool Organizer",
    "organizer/organizer-11.png": "Desktop Organizer Tray",
    "organizer/organizer-12.png": "Pen Desktop Organizer",
    "organizer/organizer-13.png": "Pencil Cup Organizer",
    "organizer/organizer-14.png": "Small Things Organiser",
    "organizer/organizer-15.png": "Cable Organizer Clip",
    "organizer/organizer-16.png": "Cable Organizer",
    "organizer/organizer-17.png": "Oreo Cable Organizer",
    "organizer/organizer-18.png": "Oreo Keychain",
    "organizer/organizer-19.png": "UNO Card Holder",
    "organizer/organizer-20.png": "UNO Card Box",
    "keychains/keychain-gift-01.png": "Super Mommy Gift Name Plate",
    "keychains/keychain-gift-02.png": "Super Mario Figure",
    "keychains/keychain-gift-03.png": "Toad Super Mario Figure",
    "keychains/keychain-gift-04.png": "Mini Toy Figure Set",
    "keychains/keychain-gift-05.png": "Dragon Figure",
    "keychains/keychain-gift-06.png": "Flexi T-Rex",
    "keychains/keychain-gift-07.png": "Dino Balance Game Box",
    "keychains/keychain-gift-08.png": "Ghost Gamer Mini Figure",
    "keychains/keychain-gift-09.png": "Cute Mini Octopus Set",
    "keychains/keychain-gift-10.png": "Mini Octopus",
    "keychains/keychain-gift-11.png": "Zootopia Nick Wilde Articulated Figure",
    "keychains/keychain-gift-12.png": "Pikachu Figure",
    "keychains/keychain-gift-13.png": "Sleeping Pikachu Figure",
    "keychains/keychain-gift-14.png": "Pikachu Keychain",
    "keychains/keychain-gift-15.png": "Pokeball Keychain Pair",
    "custom-names/custom-name-01.png": "Custom Name Wall Letters",
    "custom-names/custom-name-02.png": "Custom Name Keychain Set",
    "custom-names/custom-name-03.png": "Custom Name Tags",
    "custom-names/custom-name-04.png": "Flat Is Boring Name Plate",
    "custom-names/custom-name-05.png": "Love You Custom Name Plate",
    "custom-names/custom-name-06.png": "Sweeping Name Plate",
    "custom-names/custom-name-07.png": "Initial Letter Name Stand",
    "custom-names/custom-name-08.png": "Color Custom Name Keychains",
}


def readable_name(path):
    product_name = PRODUCT_NAMES.get(path.as_posix())
    if product_name:
        return product_name
    words = path.stem.replace("_", " ").replace("-", " ").split()
    cleaned = [word for word in words if not word.lower().startswith(("img", "dsc", "pxl"))]
    title = " ".join(cleaned or words).title()
    return title[:70] or "Custom 3D Print"


def stable_price(category, image_path):
    low, high = CATEGORY_PRICE_RANGES.get(category, (249, 999))
    rng = Random(str(image_path))
    step = 10
    return rng.randrange(low // step, high // step + 1) * step + 9


def image_rng(relative):
    return Random(relative)


def unique_slug(base):
    slug = slugify(base)[:180] or "product"
    original = slug
    counter = 2
    while Product.objects.filter(slug=slug).exists():
        slug = f"{original}-{counter}"[:200]
        counter += 1
    return slug


class Command(BaseCommand):
    help = "Seed every product image into the XTRUDE 3D catalog"

    def handle(self, *args, **options):
        root = settings.ROOT_DIR / "productsimg"
        seeded = 0

        mini = root / "minime.jpg"
        if mini.exists():
            Product.objects.update_or_create(
                slug="mini-me-custom-figure",
                defaults={
                    "name": "Mini Me Custom Figure",
                    "category": "Mini Me",
                    "price": 0,
                    "image": "minime.jpg",
                    "description": "Fully customized 3D miniature from your photo. Quote shared on WhatsApp.",
                    "material": "Resin / PLA",
                    "weight_grams": 350,
                    "is_featured": True,
                    "is_custom": True,
                    "stock": 20,
                },
            )
            seeded += 1

        for folder, category in CATEGORY_LABELS.items():
            category_dir = root / folder
            if not category_dir.exists():
                continue
            for image in sorted(category_dir.iterdir()):
                if image.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                relative = image.relative_to(root).as_posix()
                existing = Product.objects.filter(image=relative).first()
                name = existing.name if existing else readable_name(Path(relative))
                rng = image_rng(relative)
                Product.objects.update_or_create(
                    image=relative,
                    defaults={
                        "name": name,
                        "slug": existing.slug if existing else unique_slug(f"{category}-{name}"),
                        "category": category,
                        "price": existing.price if existing else stable_price(category, image),
                        "description": f"3D printed {category.lower()} item ready for order or customization.",
                        "material": existing.material if existing else MATERIALS[rng.randrange(len(MATERIALS))],
                        "weight_grams": existing.weight_grams if existing else rng.randrange(180, 801),
                        "rating": existing.rating if existing else 4.5 + (rng.randrange(0, 5) / 10),
                        "is_featured": existing.is_featured if existing else seeded % 9 == 0,
                        "is_custom": category in {"Projects", "Custom Names"},
                        "stock": existing.stock if existing else 20,
                    },
                )
                seeded += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded/updated {seeded} products from productsimg."))
