import logging
from rest_framework.response import Response
from .models import Profile
from .serializers import ProfileSerializer

from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import ( # Миксины для ограничения доступа к класс-представлениям (views).
    LoginRequiredMixin,  # Требует, чтобы пользователь был авторизован (вошёл в систему).
    PermissionRequiredMixin,  # Требует наличия у пользователя определённого разрешения (permission).
    UserPassesTestMixin  # Позволяет задать собственную функцию проверки (test_func),
)


logger = logging.getLogger(__name__) # Создаем логгер

class ProfileDetailView(RetrieveUpdateAPIView):
    """
    Представление обрабатывает запрос на получение одного, текущего профиля

    Доступ разрешён только авторизованным пользователям.
    Если пользователь не найден — возвращается 404.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]


    def get_object(self):
        current_user = self.request.user
        logger.info(f"Текущий юзер: {current_user}")
        profile = Profile.objects.get(user__username=current_user.username)
        return profile

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)