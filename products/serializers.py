from typing import Any

from rest_framework import serializers  # Импортируем модуль сериализаторов DRF
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product.
    Преобразует объекты Product <-> JSON.
    Используется для чтения, создания, обновления и удаления товаров
    """
    images = serializers.SerializerMethodField()
    class Meta: # Класс конфигурации сериализатора
        model = Product # Указываем, с какой моделью работает сериализатор
        fields = [ # Перечисляем поля, которые попадут в JSON
            "id",
            "title",
            "short_description",
            "description",
            "price",
            "images",
            "is_limited",
            "sorting_index",
            "purchases_count",
            "is_active",
            "created_at",
        ]

    def get_images(self, odj: {images}) -> list[dict[str, Any]] | list:
        """
        Метод вернет список изображений в формате [{"src": url, "alt": name}]
        """
        if odj.images:
            return [
                {
                    "src": odj.images.url,
                    "alt": odj.title,
                 }
            ]
        return []