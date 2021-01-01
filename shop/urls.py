from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path

from . import views

app_name = 'shop'
urlpatterns = [
    path("shop/additem/", views.additem, name="additem"),
    path("shop/removeitem/", views.removeitem, name="removeitem"),
    path("shop/removecartitem/", views.removecartitem, name="removecartitem"),
    path("shop/checkout/", views.checkout, name="checkout"),
    path("shop/recent_orders/", views.recent_orders, name="recent_orders"),
    path("shop/checkout/", views.checkout, name="checkout"),
    path("shop/payment/", views.payment, name="payment"),
    path("shop/addaddress/", views.addaddress, name="addaddress"),
    path("shop/removeaddress/", views.removeaddress, name="removeaddress"),
    path("shop/order/<int:id>/", views.order_success, name="order-success"),
    path("shop/email_preview/<int:id>/", views.email_preview, name="email_preview"),
    path("privacy_policy/", views.privacy_policy, name="privacy_policy"),

]
