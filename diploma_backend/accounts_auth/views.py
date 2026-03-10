import json
import logging

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__) # Создаем логгер

class SignUp(APIView):
    """
    Класс представление для создания\регистрации пользователя
    """
    # разрешение, доступ для любого пользователя
    permission_classes = [AllowAny]

    def post(self, request):
        data = json.loads(request.body)
        logger.info(f"тело запроса с данными регистрации пользователя: {data}")

        name = data.get('name')
        username = data.get('username')
        password = data.get('password')
        # Проверяем что такого пользователя еще не существует, иначе бросаем 409
        if User.objects.filter(username=username).exists():
            return Response({"error": "user already exists"}, status=409)
        # если такого пользователя еще нет, создаем его
        user = User.objects.create_user(
            username=username,
            password=password
        )
        user.first_name = name
        user.save()
        logger.info(f"Создан новый пользователь: {user.first_name}")
        # Сразу логиним нового пользователя
        if user.is_active:
            login(request=request, user=user)

        return Response({"status": "ok"}, status=200)


class SingIn(APIView):
    """
    Представление для аутентификации\входа юзера на сайт
    """
    # разрешение, доступ для любого пользователя
    permission_classes = [AllowAny]

    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        logger.info(f"Данные авторизации: {username}\n{password}")

        user = authenticate(
            username=username,
            password=password
        )
        # проверяем что пользователь существует и пароль верный
        # так же проверяем что учетная запись не деактивирована
        if user is not None and user.is_active:
            # если пользователь и пароль верны логиним его в системе
            login(request=request, user=user)
            return Response({"status": "ok"}, status=200)
        else:
            return Response({"error": "Incorrect login or password"}, status=401)


class SingOut(APIView):
    """
    Представление для разлогинивани пользователя
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request=request)
        return Response({"status": "ok"}, status=200)