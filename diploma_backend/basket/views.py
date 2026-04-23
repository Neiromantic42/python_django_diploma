import logging

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import Basket
from .serializers import BasketSerializer

logger = logging.getLogger(__name__)


class BasketProductsListApiView(APIView):
    """
    Представление для получения корзины, текущего юзера

    со всеми товарами\позициями
    """
    # Закоментируем это ограничение пока что любой пользователь может получить доступ к корзине
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_anonymous:
            basket = Basket.objects.filter(user=request.user)
            serializer = BasketSerializer(basket, many=True)
            return Response(serializer.data)
        else:
            cart = request.session.get("cart", [])
            # собираем все id product
            product_ids = [item['product_id'] for item in cart]
            # Загружаем ВСЕ товары одним запросом
            products = Product.objects.filter(
                id__in=product_ids
            ).select_related(
                'category'
            ).prefetch_related(
                'images',
                'tags',
                'reviews'
            ).annotate(
                avg_rating=Avg("reviews__rate")
            )
            # Создаем словарь {id: count} из корзины
            cart_dict = {item['product_id']: item['count'] for item in cart}
            response_data = []
            for product in products:
                response_data.append({
                    "id": product.id,
                    "category": product.category.id,
                    "price": product.price,
                    "count": cart_dict[product.id],
                    "date": product.date,
                    "title": product.title,
                    "description": product.description,
                    "freeDelivery": product.free_delivery,
                    "images": [{"src": img.src.url, "alt": img.alt} for img in product.images.all()],
                    "tags": [{"id": tag.id, "name": tag.name} for tag in product.tags.all()],
                    "reviews": product.reviews.count(),
                    "rating": round(product.avg_rating, 2) if product.avg_rating else 0
                })
        return Response(response_data, status=200)

    def post(self, request):
        # получаем необходимые данные из тела запроса
        user = request.user
        product_id = request.data["id"]
        count = request.data["count"]
        # Если пользователь не анонимен(авторизован)
        if not user.is_anonymous:
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
                user=user, product=product, defaults={"count": count}
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
        # если пользователь анонимен(не авторизован)
        else:
            cart = request.session.get("cart", [])
            # Проверяем, есть ли уже этот товар в корзине
            found = False
            for item in cart:
                if item["product_id"] == product_id:
                    item["count"] += count
                    found = True
                    break
                # Если товара ещё нет, добавляем новый словарь
            if not found:
                cart.append({"product_id": product_id, "count": count})
            # Сохраняем корзину обратно в сессию
            request.session["cart"] = cart
            request.session.modified = True
            product_ids = [item['product_id'] for item in cart]
            # Загружаем ВСЕ товары одним запросом
            products = Product.objects.filter(
                id__in=product_ids
            ).select_related(
                'category'
            ).prefetch_related(
                'images',
                'tags',
                'reviews'
            ).annotate(
                avg_rating=Avg("reviews__rate")
            )
            # Создаем словарь {id: count} из корзины
            cart_dict = {item['product_id']: item['count'] for item in cart}
            response_data = []
            for product in products:
                response_data.append({
                    "id": product.id,
                    "category": product.category.id,
                    "price": product.price,
                    "count": cart_dict[product.id],
                    "date": product.date,
                    "title": product.title,
                    "description": product.description,
                    "freeDelivery": product.free_delivery,
                    "images": [{"src": img.src.url, "alt": img.alt} for img in product.images.all()],
                    "tags": [{"id": tag.id, "name": tag.name} for tag in product.tags.all()],
                    "reviews": product.reviews.count(),
                    "rating": round(product.avg_rating, 2) if product.avg_rating else 0
                })
        return Response(response_data, status=200)

    def delete(self, request, *args, **kwargs):
        # получаем необходимые данные из тела запроса
        user = request.user
        if not user.is_anonymous:
            product_id = request.data["id"]
            count = request.data["count"]

            logger.info(
                f"User: {user.first_name}"
                f"\nproduct_pk: {product_id}"
                f"\nproduct_count: {count}"
            )
            # Получаем одну запись из таблицы Basket у текущего юзера и товаром
            cart_position = get_object_or_404(Basket, user=user, product_id=product_id)
            # Проверяем, если кол-во товара в корзине меньше или равно поданному с фронта count:
            if cart_position.count <= count:
                # То удаляем запись из корзины товаров
                cart_position.delete()
            else:  # а иначе уменьшаем кол-во товара в корзине на count
                cart_position.count -= count
                cart_position.save()
            # получаем все записи из Корзины(Basket)
            baskets = Basket.objects.filter(user=user)
            # сериализуем обьекты корзины(записи в ней) и возвращаем на фронт
            serializer = BasketSerializer(baskets, many=True)
            return Response(serializer.data)
        else:
            cart = request.session.get("cart", [])
            logger.info(f"Данные корзины из сесии: {cart}")
            request_data = request.data
            logger.info(f"Данные на удаление из запроса: {request_data}")
            for item in cart:
                if item["product_id"] == request_data["id"]:
                    if item["count"] <= request_data["count"]:
                        cart.remove(item)
                        break
                    else:
                        item["count"]-=request_data["count"]
                        break
            request.session["cart"] = cart
            request.session.modified = True
            logger.info(f"Данные корзины в сесии после уменьшения\удаления товара: {cart}")
            # получаем id всех отваров из корзины в сесии
            products_ids = [item["product_id"] for item in cart]
            # загружаем все товары и связные сущности одним запросом из бд
            products = Product.objects.filter(
                id__in=products_ids
            ).select_related(
                'category'
            ).prefetch_related(
                'images',
                'tags',
                'reviews'
            ).annotate(
                avg_rating = Avg("reviews__rate")
            )
            # Создаем словарь {id: count} из корзины
            cart_dict = {item['product_id']: item['count'] for item in cart}
            logger.info(f"Данные словаря корзины: {cart_dict}")
            response_data = []
            for product in products:
                response_data.append({
                    "id": product.id,
                    "category": product.category.id,
                    "price": product.price,
                    "count": cart_dict[product.id],
                    "date": product.date,
                    "title": product.title,
                    "description": product.description,
                    "freeDelivery": product.free_delivery,
                    "images": [
                        {
                            "src": img.src.url if img.src else None,
                            "alt": img.alt if img.alt else ""
                        }
                        for img in product.images.all()
                    ],
                    "tags": [
                        {
                            "id": tag.id if tag else None,
                            "name": tag.name if tag else None
                        }
                        for tag in product.tags.all()
                    ],
                    "reviews": product.reviews.count(),
                    "rating": round(product.avg_rating, 2) if product.avg_rating else 0
                })
            return Response(response_data, status=200)