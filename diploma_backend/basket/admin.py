from django.contrib import admin
from .models import Basket

@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    """
    Настройка отображения модели корзина в админке
    """
    list_display = (
        "id",
        "user",
        "product",
        "count"
    )
    search_fields = ("user", "product")
