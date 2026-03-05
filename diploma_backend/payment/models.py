from django.db import models
from orders.models import Order
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator



class Payment(models.Model):
    """
    Модель оплаты (Payment)

    Хранит попытки оплаты заказа
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='Попытки оплаты заказа',
    )
    card_number = models.CharField(
        max_length=16,
        null=False,
        blank=False,
    )
    month = models.CharField(
        max_length=2,
        validators=[RegexValidator(r'^(0[1-9]|1[0-2])$', message='Месяц должен быть от 01 до 12')],
        verbose_name='Месяц годности карты'
    )
    year = models.IntegerField(
        validators=[MinValueValidator(26), MaxValueValidator(36)],
        verbose_name="Дата годности карты (год)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата попытки оплаты'
    )
    code = models.CharField(
        max_length=3,
        validators=[RegexValidator(r'^\d{3}$', message='Код должен быть 3 цифры')],
        verbose_name='CVV / код безопасности'
    )
    status_payment = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'В ожидании'),
            ('success', 'Оплачено'),
            ('failed', 'Ошибка')
        ],
        default='pending',
        verbose_name='статус оплаты'
    )
    error_message = models.TextField(blank=True, null=True, verbose_name='текст ошибки')


