from django.contrib import admin
from .models import Order, OrderProduct

class OrderProductInline(admin.TabularInline):
    """
    Inline для отображения товаров в заказе внутри Order
    """
    model = OrderProduct
    extra = 0
    readonly_fields = ("price",)
    can_delete = True

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Настройка отображения модели Order в админке
    """
    list_display = (
        "id",
        "user",
        "created_at",
        "full_name",
        "email",
        "phone",
        "delivery_type",
        "payment_type",
        "total_cost",
        "status",
        "city",
        "address",
    )
    list_filter = ("status", "delivery_type", "payment_type", "created_at")
    search_fields = ("full_name", "email", "phone", "city", "address", "user__username")
    inlines = [OrderProductInline] # показываем связанные товары

    @admin.display(description="Имя клиента")
    def full_name_display(self, odj: Order):
        return odj.full_name or odj.user.get_full_name()


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    """
    Отдельная админка для OrderProduct на случай, если нужно управлять напрямую
    """
    list_display = (
        "id",
        "order",
        "product",
        "count",
        "price",
    )
    list_filter = ("order", "product")
    search_fields = ("product__title", "order__id")

