from rest_framework import serializers  # Импортируем модуль сериализаторов DRF
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Profile.

    Преобразует объекты Profile <-> JSON.
    Используется для чтения, создания, обновления и удаления профиля
    """
    fullName = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "fullName",
            "email",
            "phone",
            "avatar"
        ]

    def get_fullName(self, obj: Profile):
        """
        Метод вернет полное имя юзера
        """
        return obj.user.get_full_name()

    def get_email(self, obj: Profile):
        """
        Метод вернет email юзера
        """
        return obj.user.email

    def get_avatar(self, obj: Profile):
        """
        Метод вернет аватар профиля
        """
        if hasattr(obj, "images"):
            return {
                "src": obj.images.src.url,
                "alt": obj.images.alt or ""
            }
        return {
            "src": None,
            "alt": ""
        }
