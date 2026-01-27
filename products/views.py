import logging

from django.views import View
from django.views.generic import (
    ListView,       # список объектов
    DetailView,     # детали одного объекта
    CreateView,     # создание нового объекта
    UpdateView,     # редактирование существующего объекта
    DeleteView      # удаление объекта
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Product

from django.http import HttpResponse, HttpRequest, JsonResponse, \
    HttpResponseRedirect  # Импортируем класс HttpResponse, чтобы возвращать простой HTTP-ответ (текст, HTML и т.д.)

from django.shortcuts import render, redirect, reverse, get_object_or_404

from .serializers import ProductSerializer

log = logging.getLogger(__name__) # Создаем логгер

class ProductsLimitedListView(ModelViewSet):
    """
    Представление для получения списка лимитированных товаров.


    Возвращает JSON-ответ со списком объектов товаров, каждый из которых содержит:
    - id: int — идентификатор товара
    - title: str — название товара
    - price: Decimal — цена товара
    - images: List[Dict[str, str]] — список изображений товара, каждый словарь содержит:
    - src: str — абсолютный путь к изображению
    - alt: str — альтернативный текст
    """
    queryset = (
        Product
        .objects
        .filter(is_limited=True)
        .order_by("sorting_index", "-purchases_count")[:8]
    )
    serializer_class = ProductSerializer

