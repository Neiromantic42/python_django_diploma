from django.urls import path

from .views import (
    order_create, # по GET возвращает список заказов, по POST создает заказ
    order_detail, # по GET вернет конкретный заказ, по POST обновит его
)

urlpatterns = [
    # Создание заказа (POST) / Получение всех заказов текущего пользователя (GET)
    path('orders', order_create, name="orders-list-create"),

    # Получение конкретного заказа (GET) / Подтверждение / обновление заказа (POST)
    path('order/<int:id>', order_detail, name="order-detail-update"),
]
