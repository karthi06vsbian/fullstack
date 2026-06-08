from pathlib import Path
from random import Random

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from store.models import Product


CATEGORY_LABELS = {
    "home-decor": "Home Decor",
    "keychains": "Keychains",
    "pets": "Pets",
    "projects": "Projects",
    "toys": "Toys",
    "useful-appliances": "Useful Appliances",
}

CATEGORY_PRICE_RANGES = {
    "Home Decor": (349, 1299),
    "Keychains": (129, 449),
    "Pets": (199, 799),
    "Projects": (699, 2499),
    "Toys": (199, 999),
    "Useful Appliances": (249, 1199),
}

MATERIALS = ["PLA", "Matte PLA", "Silk PLA", "PETG"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def readable_name(path):
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
    help = "Seed every product image into the PrintForge catalog"

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
                name = existing.name if existing else readable_name(image)
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
                        "is_custom": category == "Projects",
                        "stock": existing.stock if existing else 20,
                    },
                )
                seeded += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded/updated {seeded} products from productsimg."))
