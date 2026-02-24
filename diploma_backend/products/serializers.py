from django.db.models import Avg
from rest_framework import serializers  # Импортируем модуль сериализаторов DRF
from .models import Product, Category, Review, Sale


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product.

    Преобразует объекты Product <-> JSON.
    Используется для чтения, создания, обновления и удаления товаров
    """
    price = serializers.SerializerMethodField()
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


    def get_price(self, obj: Product):
        """
        Метод вернет цену(price) с учетом скидки, если она есть
        """
        if hasattr(obj, 'sale') and obj.sale:
            return obj.sale.sale_price
        return obj.price


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
        # return obj.reviews.count()
        return obj.reviews_count


    def get_rating(self, obj: Product):
        """
        Метод вернет средний рейтинг товара
        """
        # return obj.reviews.aggregate(avg=Avg('rate'))['avg'] or 0
        return obj.avg_rating or 0


class ProductDetailSerializer(ProductSerializer):
    """
    Служит для обработки запроса конкретного продукта

    GET /product{id}
    Наследует поля от ProductSerializer
    """
    fullDescription = serializers.CharField(source='full_description')
    tags = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            "fullDescription",
            "tags",
            "reviews",
            "specifications",
        ]


    def get_tags(self, obj: Product):
        """
        Метод вернет теги товара в формате ["string"]
        """
        return [tag.name for tag in obj.tags.all()] or []


    def get_specifications(self, obj: Product):
        """
        метод вернет спецификацию товара в формате [{"name": "size"...}...]
        """
        return [
            {
                "name": spec.name,
                "value": spec.value
            }
            for spec in obj.specifications.all()
        ]


    def get_reviews(self, obj: Product):
        """
        метод вернет отзывы в формате [{"author": "Annoying Orange",},...]
        """
        return [
            {
                "author": review.author,
                "email": review.email,
                "text": review.text,
                "rate": review.rate,
                "date": review.date
            }
            for review in obj.reviews.all()
        ]


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
        sub = obj.subcategories.all() # обращаемся ко всем активным подкатегориям
        # рекурсивно вызываем CategorySerializer и передаем в контекст уровень вложенности
        return CategorySerializer(sub, many=True, context={"level": level + 1}).data or []


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review.

    Преобразует объекты Review <-> JSON.
    """
    class Meta:
        model = Review
        fields = [
            "author",
            "email",
            "text",
            "rate",
            "date"
        ]


class SalesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Sale

    Преобразует объекты Sale <-> JSON
    Используется для получения сериализованых обьектов Sale(скидок\акций с товарами)
    """
    id = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    salePrice = serializers.FloatField(source="sale_price")
    dateFrom = serializers.SerializerMethodField(source="date_from")
    dateTo = serializers.SerializerMethodField(source="date_to")
    images = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = [
            "id",
            "price",
            "salePrice",
            "dateFrom",
            "dateTo",
            "images"
        ]

    def get_id(self, obj: Sale):
        """
        Метод вернет id товара сос кидкой
        """
        if obj.product:
            return str(obj.product.pk)


    def get_price(self, obj: Sale):
        """
        Метод вернет цену(price) без учета скидки
        """
        if hasattr(obj, 'product') and obj.product:
            return float(obj.product.price)
        return None


    def get_dateFrom(self, obj: Sale):
        # приводим дату к требуемому сваггер виду
        return obj.date_from.strftime("%m-%d") if obj.date_from else None

    def get_dateTo(self, obj: Sale):
        # приводим дату к требуемому сваггер виду
        return obj.date_to.strftime("%m-%d") if obj.date_to else None


    def get_images(self, obj: Sale):
        """
        Метод вернет список изображений в формате [{"src": url, "alt": name}]
        """
        if obj.product and obj.product.images.exists():
            return [
                {
                    "src": img.src.url,
                    "alt": img.alt or "",
                }
                for img in obj.product.images.all()
            ]
        return []