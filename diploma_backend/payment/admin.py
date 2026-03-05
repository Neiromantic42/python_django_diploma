from django.contrib import admin
from .models import Payment



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Настройка отображения Сущности(модели)-оплаты(Payment)
    """
    list_display = (
        'id',
        'order',
        'card_number',
        'month',
        'year',
        'created_at',
        'code',
        'status_payment',
        'short_error_message'
    )
    list_filter = ('status_payment', 'created_at')
    search_fields = ('order__id', 'card_number')

    @admin.display(description="Короткий текст ошибки")
    def short_error_message(self, obj: Payment):
        return obj.error_message[:50] + '...' if obj.error_message else ''


