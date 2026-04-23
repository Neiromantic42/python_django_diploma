import re
from datetime import datetime

from rest_framework import serializers

from payment.models import Payment


class PaymentsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания оплаты

    И валидации данных оплаты
    """

    number = serializers.CharField(source="card_number")
    name = serializers.CharField(source="card_holder_name")

    class Meta:
        model = Payment
        fields = [
            "number",
            "name",
            "month",
            "year",
            "code",
        ]

    def validate_name(self, value):
        """
        Валидируем ФИО держателя карты
        """
        # Длина имени не может быть меньше 2х слов
        value = value.strip()  # убираем лишние пробелы в конце и начале строки
        words = value.split()  # разделяем по пробелу в середине строки
        if len(words) < 2:
            raise serializers.ValidationError("недостаточно данных в поле ФИО")
        # Только буквы, пробелы, дефисы, апострофы
        if not re.match(r"^[A-Za-zА-Яа-яЁё\s\-\']+$", value):
            raise serializers.ValidationError("ФИО может содержать только буквы")

        return value

    def validate_number(self, value):
        """
        Валидируем номер карты
        """
        if not value.isdigit():
            raise serializers.ValidationError(
                "Номер карты должен содержать только цифры"
            )
        if len(value) != 8:
            raise serializers.ValidationError(
                "Длинна номера карты должна быть ровно 8 цифр"
            )

        return value

    def validate_month(self, value):
        """
        Валидируем месяц карты
        """
        if not value.isdigit():
            raise serializers.ValidationError("Месяц может содержать только цифры")

        month = int(value)
        if 1 > month or month > 12:
            raise serializers.ValidationError(
                "Номер месяца может лежать в диапазоне от 1 до 12 включительно"
            )

        return value

    def validate_year(self, value):
        """
        Валидируем год окончания срока службы карты
        """
        str_value = str(value)

        if not str_value.isdigit():
            raise serializers.ValidationError("Год может состоять только из цифр")

        year = int(value)
        current_yar_short = int(datetime.now().strftime("%y"))
        if year < current_yar_short or year > (current_yar_short + 10):
            raise serializers.ValidationError(
                f"Год карты должен быть в диапазоне от"
                f" {current_yar_short} до {current_yar_short + 10}"
            )
        return value

    def validate_code(self, value):
        """
        Валидируем код CSV
        """
        if not value.isdigit():
            raise serializers.ValidationError("CSV - код может содержат только цифры")
        if len(value) != 3:
            raise serializers.ValidationError("CSV-код должен содержать ровно 3 цифры")
        return value
