from decimal import Decimal
from django.db.models.aggregates import Avg
from rest_framework import serializers  # Импортируем модуль сериализаторов DRF
from django.contrib.auth.models import User
from products.models import Product
from .models import Order, OrderProduct
from products.serializers import ProductSerializer


class OrderProductInputSerializer(serializers.Serializer):
    """
    Сериализатор для валидации входящих обьектов продуктов в запросе POST/order
    """
    id = serializers.IntegerField()
    count = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Product with id {value} does not exist")
        return value


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания заказа
    """
    products = OrderProductInputSerializer(many=True)

    class Meta:
        model = Order
        fields = ['products']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        user = self.context['request'].user
        order = Order.objects.create(user=user)

        total_cost = 0
        for item in products_data:
            product = Product.objects.get(pk=item['id'])
            count = item['count']
            price = product.price
            total_cost += price * count
            OrderProduct.objects.create(
                order=order,
                product=product,
                count=count,
                price=price
            )

        order.total_cost = total_cost
        order.save()
        return order


class OrderProductsSerializer(ProductSerializer):
    """
    Сериализатор вернет список товаров

    с актуальной ценой и количеством из заказа
    """
    reviews = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    def to_representation(self, instance):
        # instance = OrderProduct
        data = super().to_representation(instance.product)
        data['price'] = instance.price
        data['count'] = instance.count
        return data


    def get_reviews(self, obj: Product):
        """
        Переопределяем метод родителя get_reviews
        возвращает количество отзывов на товаре
        """
        return obj.reviews.count()

    def get_rating(self, obj: Product):
        """
        Переопределяем метод родителя get_rating
        Возвращает рейтинг товара
        """
        return obj.reviews.aggregate(avg=Avg('rate'))['avg']



class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для POST /order/{id}

    Вернет агрегированные данные заказа
    """
    createdAt = serializers.DateTimeField(source="created_at")
    fullName = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    deliveryType = serializers.CharField(source="delivery_type", max_length=20)
    paymentType = serializers.CharField(source="payment_type")
    totalCost = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products"
        ]


    def get_fullName(self, obj: Order):
        """
        метод вернет last_name + middle_name + first_name
        """
        if obj.full_name:
            return obj.full_name
        elif hasattr(obj.user, "profile"):
            full_name = [obj.user.last_name, obj.user.first_name, obj.user.profile.middle_name]
            return " ".join(filter(None, full_name))
        else:
            return " ".join(filter(None, [obj.user.last_name, obj.user.first_name]))


    def get_email(self, obj: Order):
        """
        Метод вернет email из заказа, если есть, иначе email юзера
        """
        if obj.email:
            return obj.email
        else:
            return obj.user.email


    def get_phone(self, obj: Order):
        """
        Метод вернет phone из заказа, если есть, иначе phone юзера
        """
        if obj.phone:
            return str(obj.phone)
        elif hasattr(obj.user, "profile") and obj.user.profile.phone:
            return str(obj.user.profile.phone)
        else:
            return ""


    def get_totalCost(self, obj: Order):
        """
        Метод вернет общую сумму заказа
        """
        if obj.total_cost == 0:
            products = obj.products.all()
            total_cost = Decimal('0')
            for product in products:
                total_price = product.count * product.price
                total_cost += total_price
            return total_cost
        else:
            return obj.total_cost


    def get_products(self, obj: Order):
        """
        Метод вернет список товаров с актуальной ценой, и количеством из заказа
        """
        order_products = obj.products.all()
        return OrderProductsSerializer(order_products, many=True).data


class ConfirmOrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подтверждения\обновления заказа
    """
    class Meta:
        model = Order
        fields = [
            "full_name",
            "email",
            "phone",
            "delivery_type",
            "payment_type",
            "status",
            "city",
            "address",
        ]

    def update(self, instance, validated_data):
        # instance - существующий объект из БД Order
        # validated_data - провалидированные данные из запроса
        instance.full_name = validated_data.get('fullName', instance.full_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.delivery_type = validated_data.get('deliveryType', instance.delivery_type)
        instance.status = 'accepted'
        instance.city = validated_data.get('city', instance.city)
        instance.address = validated_data.get('address', instance.address)
        instance.payment_type = validated_data.get('paymentType', instance.payment_type)
        instance.save() # сохраняем изменения
        return instance