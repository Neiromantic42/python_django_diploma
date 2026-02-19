from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, ImagesProfile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор профиля пользователя.

    Назначение:
    - Отдаёт данные профиля в формате, который ожидает фронтенд.
    - Принимает данные от фронтенда и обновляет:
        • модель Profile
        • связанную модель User

    Особенность:
    fullName и email хранятся в модели User,
    phone — в Profile,
    avatar — связан через images.

    Поэтому логика чтения и обновления разделена:
    - to_representation() отвечает за формат GET
    - update() отвечает за сохранение POST
    """

    # Поля для записи (POST)
    # Они позволяют сериализатору принять входящие данные
    fullName = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    avatar = serializers.DictField(required=False)

    class Meta:
        model = Profile
        fields = [
            "fullName",
            "email",
            "phone",
            "avatar"
        ]

    def validate_email(self, value):
        if (User.objects.filter(email=value)
                .exclude(pk=self.instance.user.pk if self.instance else None)
                .exists()
        ):
            raise serializers.ValidationError(f"Пользователь с таким email: {value} уже зарегистрирован")
        return value

    def to_representation(self, instance: Profile):
        """
        Метод вызывается автоматически при GET запросе.
        Он преобразует объект модели (Profile) в JSON.

        instance — это конкретный объект Profile.
        """

        # Вспомогательная функция для сборки ФИО
        # Берем фамилию, имя и отчество (если есть)
        def get_full_name(user, instance):
            parts = [
                user.last_name,
                user.first_name,
                getattr(instance, "middle_name", "")
            ]
            # filter(None, parts) убирает пустые строки
            # join объединяет через пробел
            return " ".join(filter(None, parts))

        # super().to_representation(instance)
        # DRF сначала сам формирует словарь по Meta.fields
        data = super().to_representation(instance)

        # Переопределяем значения так,
        # как их ожидает фронтенд

        data['fullName'] = get_full_name(
            user=instance.user,
            instance=instance
        )

        # Email хранится в модели User
        data['email'] = instance.user.email

        # Приводим phone к строке (если None — возвращаем пустую строку)
        data['phone'] = str(instance.phone) if instance.phone else ""

        # Формируем объект avatar
        # hasattr проверяет есть ли связанный объект images
        data['avatar'] = {
            "src": instance.images.src.url if hasattr(instance, "images") else None,
            "alt": instance.images.alt if hasattr(instance, "images") else ""
        }

        return data

    def update(self, instance, validated_data):
        """
        Метод вызывается при POST / PUT / PATCH.
        validated_data — это уже проверенные сериализатором данные.

        instance — существующий объект Profile.
        """

        # Получаем данные из запроса (если они есть)
        fullName = validated_data.get("fullName")
        email = validated_data.get("email")
        phone = validated_data.get("phone")

        # --- Обновление ФИО ---
        if fullName:
            # Убираем лишние пробелы и делим строку максимум на 3 части
            parts = fullName.strip().split(" ", 2)

            # Фамилия
            instance.user.last_name = parts[0] if len(parts) > 0 else ""

            # Имя
            instance.user.first_name = parts[1] if len(parts) > 1 else ""

            # Отчество (если передано)
            instance.middle_name = parts[2] if len(parts) > 2 else ""

        # --- Обновление email ---
        if email:
            instance.user.email = email

        # --- Обновление телефона ---
        if phone:
            instance.phone = phone

        # Важно:
        # Сохраняем сначала User, потом Profile
        instance.user.save()
        instance.save()

        return instance


class AvatarSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Аватар
    """

    avatar = serializers.ImageField(source='src')

    class Meta:
        model = ImagesProfile
        fields = [
            'avatar',
            'alt'
        ]

    def validate_avatar(self, value):
        max_size = 2 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError("Размер файла не должен превышать 2мб")

        return value


class PasswordSerializer(serializers.Serializer):
    """
    Сериализатор для обновления пароля
    """
    currentPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(write_only=True, max_length=8, min_length=3)

    def validate_currentPassword(self, value):
        user = self.context['request'].user # получаем текущего юзера из контекста
        # проверяем текущий пароль объекта юзер и сравниваем с переданный в запросе
        if not user.check_password(value):
            # если совпадений нет бросам исключение
            raise serializers.ValidationError("Текущий пароль неверный")
        return value

    def update(self, instance: User, validated_data):
        # хешируем новый пароль методом обьекта User set_password
        instance.set_password(validated_data['newPassword'])
        instance.save() # сохраняем новы пароль
        return instance


