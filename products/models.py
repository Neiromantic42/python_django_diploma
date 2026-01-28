# from django.db import models # импорт модулей для создания моделей
#
# class Product(models.Model):
#     """
#     Модель Product представляет товар
#     """
#     class Meta:
#         verbose_name = 'Product'
#         verbose_name_plural = 'Products'
#
#     title = models.CharField(max_length=100, db_index=True)
#     category = models.ForeignKey(
#         Category, on_delete=models.CASCADE
#     )
#     description = models.TextField()
#     fullDescription = models.TextField()
#
#     price = models.DecimalField()
#     count = models.PositiveIntegerField()
#
#     freeDelivery = models.BooleanField()
#
#
#
#     def __str__(self):
#         """
#         Строковое представление экземпляра класса
#         """
#         return f"Product(pk={self.pk}, name={self.name})"
