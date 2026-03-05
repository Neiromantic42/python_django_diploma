from celery import shared_task # декоратор для создания задачи
from time import sleep # для имитации задержки
from .models import Payment # Импортируем модель оплаты


@shared_task # ← это превращает функцию в Celery задачу
def process_payment(payment_id):
    """
    Асинхронная обработка оплаты

    Эта функция выполняется НЕ в Django, а в отдельном worker процессе!
    payment_id: ID объекта Payment для обработки
    """
    # имитируем задержку в 3 секунды
    sleep(3)
    # получаем обькт оплаты(Payment) из бд
    payment = Payment.objects.select_related('order').get(pk=payment_id)

    # Далее бизнес логика проверки оплаты
    card_number = payment.card_number
    card_number_int = int(card_number)
    # Проверяем что номер не начинается на 0
    if card_number.startswith('0'):
        payment.status_payment = 'failed'
        payment.error_message = f'Карта: {card_number_int} заблокирована!'
    # Проверяем что номер не заканчивается на 0
    elif card_number.endswith('0'):
        payment.status_payment = 'failed'
        payment.error_message = f'Номер карты: {card_number_int} не может заканчиваться на 0'
    # Проверяем что номер карты четный
    elif card_number_int % 2 != 0:
        payment.status_payment = 'failed'
        payment.error_message = f'Номер карты: {card_number_int} должен быть четным!'
    # Если все проверки пройдены, ставим статус "успех\оплачено"
    else:
        payment.status_payment = 'success'

    # Сохраняем изменения оплаты в бд 1 hfp
    payment.save()

    # проверяем что оплата успешна, и меняем статус заказа на "оплачен"
    if payment.status_payment == "success":
        payment.order.status = "paid"
        payment.order.save()

    return f"Payment {payment_id}: {payment.status_payment}"