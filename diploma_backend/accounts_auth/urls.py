from django.urls import path

from .views import (  # представление для обработки запроса api/sign-up регистрации пользователя; представление для обработки запроса /api/sign-in авторизация пользователя; представление для обработки запроса /api/sign-out разлогинивание пользователя
    SignUp, SingIn, SingOut)

urlpatterns = [
    path("sign-up", SignUp.as_view(), name="registration"),
    path("sign-in", SingIn.as_view(), name="authorization"),
    path("sign-out", SingOut.as_view(), name="logout"),
]
