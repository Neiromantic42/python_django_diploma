import logging

from rest_framework import status
from rest_framework.response import Response
from .models import Profile, ImagesProfile
from .serializers import (
    ProfileSerializer,
    AvatarSerializer,
    PasswordSerializer,
)

from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    RetrieveUpdateAPIView,
    UpdateAPIView,
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
        # пробуем получить профиль, если его нет — создаём
        # profile = Profile.objects.get(user__username=current_user.username)
        profile, created = Profile.objects.get_or_create(user=current_user)
        if created:
            logger.info(f"Создан новый профиль для пользователя {current_user.username}")
            ImagesProfile.objects.create(user=current_user)
            logger.info(f"Создан ImagesProfile для профиля {profile.id}")
        return profile

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if not serializer.is_valid():
            response_data = serializer.to_representation(instance)
            response_data['errors'] = serializer.errors
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        return self.update(request, *args, **kwargs)



class AvatarUpdateApiView(UpdateAPIView):
    """
    Класс представление служит для

    обновления аватара текущего юзера
    """
    serializer_class = AvatarSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Проверяем, есть ли уже ImagesProfile, если нет — создаём
        profile = self.request.user.profile
        images, created = ImagesProfile.objects.get_or_create(
            profile=profile
        )
        if created:
            logger.info(f"Создан ImagesProfile для пользователя {self.request.user.username}")
        return images


    def post(self, request, *args, **kwargs):
        logger.info(f"FILES: {request.FILES}")
        logger.info(f"DATA: {request.data}")
        return self.update(request, *args, **kwargs)


class PasswordUpdateApiView(UpdateAPIView):
    """
    Класс представление для

    смены\обновления пароля
    """
    serializer_class = PasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)