from django.urls import path

from .views import (
    order_create,
    order_detail,
)

urlpatterns = [
    path('orders', order_create, name="order_create"),
    path('order/<int:id>/', order_detail, name="order_detail"),
    path('order/<int:id>', order_detail, name="order_confirm"),
]
