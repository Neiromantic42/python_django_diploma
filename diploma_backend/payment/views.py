import logging

from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from orders.models import Order

from .serializers import PaymentsSerializer
from .tasks import process_payment

logger = logging.getLogger(__name__)  # Создаем логгер


@api_view(["POST"])
def payment_create(request, id):
    """
    Представление служит для создания оплаты заказа
    """
    logger.info(f"Текущий юзер:{request.user}")
    logger.info(f"Данные оплаты: {request.data}")
    order_id = id
    order = get_object_or_404(
        Order,
        pk=order_id,
    )
    if order.status in [
        "paid",
    ]:
        return Response({"error": "Заказ уже оплачен"}, status=400)

    # Валидировать форму
    serializer = PaymentsSerializer(data=request.data)
    # проверяем валидность формы сериализатором
    if not serializer.is_valid():
        # если формы не валидны возвращаем ошибку и статус 400
        return Response(serializer.errors, status=400)
    # Если форма валидна создаем оплату
    payment = serializer.save(order=order, status_payment="pending")
    # Асинхронро вызываем нашу функцию (process_payment) оплаты
    task = process_payment.delay(payment.id)

    return Response(
        {
            "message": "Ждем подтверждения оплаты от платежной системы",
            "paymentId": payment.id,
        },
        status=202,
    )
