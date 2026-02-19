from django.db.models.aggregates import Avg
from rest_framework import serializers
from .models import Basket
from products.serializers import ProductSerializer


class BasketSerializer(ProductSerializer):
    """
    Сериализатор для модлели Basket

    Преобразует объекты Product <-> JSON. В рамках Basket.
    Используется для чтения, создания, обновления и удаления товаров из корзины
    """

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields

    def to_representation(self, instance: Basket):
        data = super().to_representation(instance.product)
        data['count'] = instance.count
        return data

    def get_reviews(self, obj):
        """
        Метод вернет кол-во отзывов(кол-во записей в табл Review)
        """
        return obj.reviews.count()

    def get_rating(self, obj):
        """
        Метод вернет средний рейтинг товара
        """
        return obj.reviews.aggregate(avg=Avg('rate'))['avg'] or 0