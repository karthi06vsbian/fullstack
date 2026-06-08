from django.urls import path

from . import views


urlpatterns = [
    path("health/", views.health),
    path("products/", views.products),
    path("products/<slug:slug>/", views.product_detail),
    path("shipping/", views.shipping_quote),
    path("orders/", views.create_order),
    path("orders/<int:order_id>/", views.order_detail),
    path("payments/verify/", views.verify_payment),
    path("whatsapp/", views.whatsapp_link),
    path("admin/login/", views.admin_login),
    path("admin/summary/", views.admin_summary),
    path("admin/orders/", views.admin_orders),
    path("admin/products/<int:product_id>/", views.admin_update_product),
]
