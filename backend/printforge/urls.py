from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(_request):
    return JsonResponse({
        "app": "PrintForge backend",
        "status": "ok",
        "endpoints": {
            "health": "/api/health/",
            "products": "/api/products/",
            "shipping": "/api/shipping/",
            "orders": "/api/orders/",
            "admin_summary": "/api/admin/summary/",
        },
    })


urlpatterns = [
    path("", api_root),
    path("admin/", admin.site.urls),
    path("api/", include("store.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static("/assets/", document_root=settings.ROOT_DIR / "assets")
    urlpatterns += static("/productsimg/", document_root=settings.ROOT_DIR / "productsimg")
