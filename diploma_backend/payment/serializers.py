from rest_framework import serializers
from datetime import datetime
from payment.models import Payment


class PaymentsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания оплаты

    И валидации данных оплаты
    """
    number = serializers.CharField(source='card_number')

    class Meta:
        model = Payment
        fields = [
            'number',
            'month',
            'year',
            'code',
        ]


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
            raise serializers.ValidationError(
                "Месяц может содержать только цифры"
            )

        month = int(value)
        if 1 > month or month > 12:
            raise serializers.ValidationError(
                'Номер месяца может лежать в диапазоне от 1 до 12 включительно'
            )

        return value


    def validate_year(self, value):
        """
        Валидируем год окончания срока службы карты
        """
        str_value = str(value)

        if not str_value.isdigit():
            raise serializers.ValidationError(
                "Год может состоять только из цифр"
            )

        year = int(value)
        current_yar_short = int(datetime.now().strftime('%y'))
        if year < current_yar_short or year > (current_yar_short + 10):
            raise serializers.ValidationError(
                f'Год карты должен быть в диапазоне от'
                f' {current_yar_short} до {current_yar_short + 10}'
            )
        return value


    def validate_code(self, value):
        """
        Валидируем код CSV
        """
        if not value.isdigit():
            raise serializers.ValidationError(
                'CSV - код может содержат только цифры'
            )
        if len(value) != 3:
            raise serializers.ValidationError(
                'CSV-код должен содержать ровно 3 цифры'
            )
        return value