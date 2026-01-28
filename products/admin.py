# from django.contrib import admin
# from .models import Product
#
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     """
#     Настройка отображения модели Product в админке.
#     """
#     list_display = (
#         "id",
#         "title",
#         "price",
#         "is_limited",
#         "is_active",
#         "sorting_index",
#         "purchases_count",
#         "created_at",
#         "short_description",
#         "description"
#     )
#     list_filter = ("is_limited", "is_active")
#     search_fields = ("name", "short_description")
