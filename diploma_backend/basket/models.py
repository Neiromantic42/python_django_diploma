from django.contrib.auth.models import User
from products.models import Product
from django.db import models

class Basket(models.Model):
    """
    Модель Basket представляет одну позицию в корзине пользователя.

    Каждая запись хранит:
    - пользователя, которому принадлежит позиция
    - товар (Product)
    - количество единиц этого товара (count)

    Все позиции одного пользователя формируют его корзину.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='basket',
        verbose_name='связь с пользователем: у одного юзера много позиций'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='basket',
        verbose_name="связь с продуктом: один продукт во множестве позиций"
    )
    count = models.PositiveIntegerField(default=0, verbose_name="Количество добавляемого товара")