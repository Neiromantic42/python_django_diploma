from django.contrib.auth.models import User  # Импорт встроенной модели пользователя Django
from django.db import models  # Импорт базового модуля для описания моделей
from phonenumber_field.modelfields import  PhoneNumberField


def profile_avatar_upload_to_path(instance: "ImagesProfile", filename: str) -> str:
    """
    Сохраняем файлы по папкам вида: media/profiles/profile_<id_профиля>/avatar/<имя_файла>
    """
    return "profiles/profile_{pk}/avatar/{filename}".format(
        pk=instance.profile.user.pk,
        filename=filename
    )


class Profile(models.Model):
    """
    Модель профиля, расширяющая данные стандартного пользователя
    """
    user = models.OneToOneField( # Связь с моделью юзер один к одному
        User,
        on_delete=models.CASCADE,
        related_name="profile" # Имя для обратной связи
    )
    middle_name = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="отчество"
    )
    phone = PhoneNumberField(
        null=True,
        blank=False,
        unique=True,
        region="RU",
        verbose_name="Телефон"
    )


class ImagesProfile(models.Model):
    """
    Модель ImagesProfile представляет собой аватар профиля
    """
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        verbose_name="Связь один к одному с моделью Profile",
        related_name="images"
    )
    src = models.ImageField(
        upload_to=profile_avatar_upload_to_path,
        null=True,
        blank=True,
        verbose_name="Ссылка на к файлу изображения"
    )
    alt = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Текстовое описание изображения"
    )
