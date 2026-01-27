from django.db import models # импорт модулей для создания моделей

class Product(models.Model):
    """
    Модель Product представляет товар
    """
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    title = models.CharField(max_length=100, db_index=True)
    short_description = models.CharField(max_length=200)
    description = models.TextField(
        null=False,
        blank=True,
    )
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    images = models.ImageField(upload_to="products/")
    is_limited = models.BooleanField(default=False, verbose_name="Лимитированный продукт")
    sorting_index = models.IntegerField(default=0, verbose_name="порядок сортировки")
    purchases_count = models.IntegerField(default=0, verbose_name="количество покупок")
    is_active = models.BooleanField(default=False, verbose_name="Доступность продукта")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Строковое представление экземпляра класса
        """
        return f"Product(pk={self.pk}, name={self.name})"
