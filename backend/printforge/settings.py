from pathlib import Path
import os

from corsheaders.defaults import default_headers
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
load_dotenv(BASE_DIR / ".env")
environ = os.environ

SECRET_KEY = environ.get("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "store",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "printforge.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    }
]

WSGI_APPLICATION = "printforge.wsgi.application"

database_options = {"charset": "utf8mb4"}
if os.environ.get("MYSQL_SSL_MODE", "").upper() == "REQUIRED":
    database_options["ssl"] = {}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE"),
        "USER": os.environ.get("MYSQL_USER"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD"),
        "HOST": os.environ.get("MYSQL_HOST"),
        "PORT": os.environ.get("MYSQL_PORT"),
        "OPTIONS": database_options,
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = ROOT_DIR / "productsimg"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
]
CORS_ALLOW_HEADERS = (*default_headers, "x-admin-password")

RAZORPAY_KEY_ID = environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = environ.get("RAZORPAY_KEY_SECRET", "")
SHIPROCKET_EMAIL = environ.get("SHIPROCKET_EMAIL", "")
SHIPROCKET_PASSWORD = environ.get("SHIPROCKET_PASSWORD", "")
WHATSAPP_NUMBER = environ.get("WHATSAPP_NUMBER", "919944823602")
HUB_PINCODE = environ.get("HUB_PINCODE", "641001")
HUB_CITY = environ.get("HUB_CITY", "Coimbatore")
ADMIN_PANEL_PASSWORD = environ.get("ADMIN_PANEL_PASSWORD", "xtrude@123")
