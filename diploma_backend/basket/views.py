from django.shortcuts import render
import logging
from rest_framework import status, request
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch
from django.db.models import  Avg
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView
)
from rest_framework.views import APIView

from .models import Basket
from products.models import Product
from .serializers import (
    BasketSerializer
)


logger = logging.getLogger(__name__)


class BasketProductsListApiView(APIView):
    """
    Представление для получения корзины, текущего юзера

    со всеми товарами\позициями
    """

    def get(self, request):
        basket = Basket.objects.filter(user=request.user)
        serializer = BasketSerializer(basket, many=True)
        return Response(serializer.data)


    def post(self, request):
        # получаем необходимые данные из тела запроса
        user = request.user
        product_id = request.data["id"]
        count = request.data["count"]

        logger.info(
            f"User: {user.first_name}"
            f"\nproduct_pk: {product_id}"
            f"\nproduct_count: {count}"
        )
        # получаем обьект продукта если его кол-во больше нуля, и он существует
        product = get_object_or_404(Product, id=product_id, count__gt=0)
        logger.info(f"Product_name: {product.title}")
        # Или получаем обьект корзины или создаем его с текущим юзером и продуктом
        basket_value, created = Basket.objects.get_or_create(
            user=user,
            product=product,
            defaults={"count": count}
        )
        # если же запись в корзине уже есть, обновляем кол-во товара и сохраняем
        if not created:
            basket_value.count += count
            basket_value.save()
        # получаем все позиции из корзины(обьекты Basket) у текущего юзера
        baskets = Basket.objects.filter(user=user)
        # сериализуем их в Json и возвращаем фронту
        serializer = BasketSerializer(baskets, many=True)
        return Response(serializer.data)


    def delete(self, request, *args, **kwargs):
        # получаем необходимые данные из тела запроса
        user = request.user
        product_id = request.data["id"]
        count = request.data["count"]

        logger.info(
            f"User: {user.first_name}"
            f"\nproduct_pk: {product_id}"
            f"\nproduct_count: {count}"
        )
        # Получаем одну запись из таблицы Basket у текущего юзера и товаром
        cart_position = get_object_or_404(
            Basket,
            user=user,
            product_id=product_id
        )
        # Проверяем, если кол-во товара в корзине меньше или равно поданному с фронта count:
        if cart_position.count <= count:
            # То удаляем запись из корзины товаров
            cart_position.delete()
        else: # а иначе уменьшаем кол-во товара в корзине на count
            cart_position.count -= count
            cart_position.save()
        # получаем все записи из Корзины(Basket)
        baskets = Basket.objects.filter(user=user)
        # сериализуем обьекты корзины(записи в ней) и возвращаем на фронт
        serializer = BasketSerializer(baskets, many=True)
        return Response(serializer.data)


