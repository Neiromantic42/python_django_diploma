from decimal import Decimal
from django.db.models.aggregates import Avg
from rest_framework import serializers  # Импортируем модуль сериализаторов DRF
from django.contrib.auth.models import User
from products.models import Product
from .models import Order, OrderProduct, DeliverySettings
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
            # получаем цену со скидкой
            if hasattr(product, 'sale') and product.sale:
                price = product.sale.sale_price
            else:
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

    paymentStatus = serializers.SerializerMethodField()
    paymentError = serializers.SerializerMethodField()

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
            "products",
            "paymentStatus",
            "paymentError"
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


    def get_paymentStatus(self, obj: Order):
        """
        Метод вернет поледний статус оплаты
        """
        last_payment = obj.payments.order_by('-created_at').first()
        return last_payment.status_payment if last_payment else None

    def get_paymentError(self, obj: Order):
        """
        Метод вернет ошибку оплаты если была
        """
        last_payment = obj.payments.filter(status_payment='failed').order_by('-created_at').first()
        if last_payment and last_payment.status_payment == 'failed':
            return last_payment.error_message
        return None



class ConfirmOrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подтверждения\обновления заказа
    """
    fullName = serializers.CharField(source='full_name', required=False)
    deliveryType = serializers.CharField(source='delivery_type', required=False)
    paymentType = serializers.CharField(source='payment_type', required=False)
    totalCost = serializers.DecimalField(max_digits=10, decimal_places=2, source='total_cost')

    class Meta:
        model = Order
        fields = [
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "status",
            "totalCost",
            "city",
            "address",
        ]

    def update(self, instance, validated_data):
        """
        Метод окончательно обновит данные заказа
        """
        # instance - существующий объект из БД Order
        # validated_data - провалидированные данные из запроса
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.delivery_type = validated_data.get('delivery_type', instance.delivery_type)
        # Ставим 'accepted' только если статус 'pending'!
        if instance.status == 'pending':
            instance.status = 'accepted'
        # получаем актуальные настройки для расчета стоимости доставки
        settings_delivery = DeliverySettings.objects.order_by('id').last()
        # Рассчитываем общую стоимость товара из продуктов заказа
        order_total_cost = sum(
            item.price * item.count
            for item in instance.products.all()
        )
        # рассчитываем стоимость доставки и присовокупляем ее к общей стоимости заказа
        if instance.delivery_type == "express":
            instance.total_cost = order_total_cost + settings_delivery.express_price
        elif instance.delivery_type == "ordinary":
            # проверяем порог бесплатной доставки
            if order_total_cost > settings_delivery.free_threshold:
                instance.total_cost = order_total_cost
            else:
                instance.total_cost = order_total_cost + settings_delivery.standard_price
        instance.city = validated_data.get('city', instance.city)
        instance.address = validated_data.get('address', instance.address)
        instance.payment_type = validated_data.get('payment_type', instance.payment_type)
        instance.save() # сохраняем изменения
        return instance