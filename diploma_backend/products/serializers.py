from django.db.models import Avg
from rest_framework import serializers  # Импортируем модуль сериализаторов DRF
from .models import Product, Category


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product.

    Преобразует объекты Product <-> JSON.
    Используется для чтения, создания, обновления и удаления товаров
    """
    images = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    freeDelivery = serializers.BooleanField(source="free_delivery")

    class Meta: # Класс конфигурации сериализатора
        model = Product # Указываем, с какой моделью работает сериализатор
        fields = [ # Перечисляем поля, которые попадут в JSON
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",

        ]

    def get_images(self, odj: Product) -> list[dict]:
        """
        Метод вернет список изображений в формате [{"src": url, "alt": name}]
        """
        return [
            {
                "src": img.src.url,
                "alt": img.alt or "",
             }
            for img in odj.images.all()
        ]

    def get_category(self, obj: Product):
        """
        Метод вернет категорию товара int
        """
        return obj.category.id

    def get_tags(self, obj: Product):
        """
        Метод вернет тег товара в формате [{"id": 12, "name": Gaming}]
        """
        return [
            {
                "id": tag.id,
                "name": tag.name,
            }
            for tag in obj.tags.all()
        ]

    def get_reviews(self, obj: Product):
        """
        Метод вернет кол-во отзывов(кол-во записей в табл Review)
        """
        return obj.reviews.count()


    def get_rating(self, obj: Product):
        """
        Метод вернет средний рейтинг товара
        """
        return obj.reviews.aggregate(avg=Avg('rate'))['avg'] or 0


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.

    Преобразует объекты Category <-> JSON.
    """
    image = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "title",
            "image",
            "subcategories"
        ]

    def get_image(self, odj: Category) -> dict:
        """
        Метод вернет список изображений в формате [{"src": url, "alt": name}]
        """
        if odj.image:
            return {
                "src": odj.image.src.url,
                "alt": odj.image.alt or "",
            }
        return None

    def get_subcategories(self, obj: Category):
        """
        Возвращает список подкатегорий рекурсивно
        """
        level = self.context.get("level", 1) # получаем уровень вложенности категории
        if level >= 2: # Если уровень больше двух, возвращаем пустой список
            return []
        sub = obj.subcategories.filter(is_active=True) # обращаемся ко всем активным подкатегориям
        # рекурсивно вызываем CategorySerializer и передаем в контекст уровень вложенности
        return CategorySerializer(sub, many=True, context={"level": level + 1}).data or []