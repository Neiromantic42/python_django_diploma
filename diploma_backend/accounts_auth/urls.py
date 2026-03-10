from django.urls import path

from .views import (
    SignUp, # представление для обработки запроса api/sign-up регистрации пользователя
    SingIn, # представление для обработки запроса /api/sign-in авторизация пользователя
    SingOut, # представление для обработки запроса /api/sign-out разлогинивание пользователя
)

urlpatterns = [
    path('sign-up', SignUp.as_view(), name='registration'),
    path('sign-in', SingIn.as_view(), name='authorization'),
    path('sign-out', SingOut.as_view(), name='logout')
]
