from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import (
    OrderCreateSerializer,
    OrderDetailSerializer,
    ConfirmOrderSerializer,
)
from .models import Order, OrderProduct
from products.models import Product
from basket.models import Basket
from django.shortcuts import get_object_or_404
from django.db import transaction

import logging


logger = logging.getLogger(__name__) # Создаем логгер


@api_view(['POST'])
def order_create(request):
    """
    Создание заказа с товарами
    """
    user = request.user
    logger.info(f"Создаём заказ для пользователя: {user}")

    products_data = request.data
    logger.info(f"Данные от фронта: {products_data}")

    serializer = OrderCreateSerializer(
        data={'products': products_data},
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    order = serializer.save()

    return Response({"orderId": order.id})



@api_view(['GET', 'POST'])
def order_detail(request, id):
    """
    Представление для получения конкретного заказа по 'GET' - запросу
    По 'POST' - запросу обновляем заказ согласно данным из тела запроса
    """
    # Если метод запроса GET, то возвращаем конкретный заказ
    if request.method == 'GET':
        order_pk = id
        logger.info(f"Запрошен заказ с id: {order_pk}")
        logger.info(f"Заказчик-текущий юзер: {request.user}")
        order = get_object_or_404(Order, pk=order_pk)
        serializer = OrderDetailSerializer(order)

        return Response(serializer.data)
    # Иначе, если запрос POST то,
    # обновляем данные заказа на введенные пользователем
    elif request.method == 'POST':
        with transaction.atomic():
            order = get_object_or_404(Order, pk=id)
            logger.info(f"Данные заказа от фронта: {request.data}")
            serializer = ConfirmOrderSerializer(
                order,
                data = request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # поле того как данные заказа обновлены\подтверждены
            # уменьшаем кол-во товара на складе
            for item in request.data['products']:
                product_pk = item['id']
                order_product_count = item['count']
                product = Product.objects.get(pk=product_pk)
                if product.count < order_product_count:
                    raise ValidationError({"error": f"Недостаточно тора {product.title} на складе"})
                product.count -= order_product_count
                product.save()
            # после того как заказ состоялся\обновился\подтвердился
            # удаляем товары из корзины
            Basket.objects.filter(user=request.user).delete()

            return Response({"orderId": order.id})