from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from phonenumber_field.modelfields import  PhoneNumberField


class Order(models.Model):
    """
    Модель заказа (Order)

    Экземпляр модели представляет собой единицу заказа
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = PhoneNumberField(null=True, blank=True, region="RU")
    delivery_type = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="тип доставки",
        default="free"
    )
    payment_type = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="способ оплаты",
        default="online"
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="итоговая сумма всего заказа"
    )
    status = models.CharField(max_length=20, blank=True, default='pending')
    city = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)



class OrderProduct(models.Model):
    """
    Модель товара в заказе (OrderProduct)

    Представляет конкретный товар, который был добавлен в заказ.
    Сохраняет информацию о цене и количестве на момент покупки.
    """
    order = models.ForeignKey(Order, related_name="products", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    count = models.PositiveIntegerField(verbose_name="Количество товара в заказе")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='цена товара на момент покупки'
    )