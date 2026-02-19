from django.shortcuts import render
import logging
from rest_framework import status, request
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch
from django.db.models import  Avg
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView
)
from rest_framework.views import APIView

from .models import Basket
from .serializers import (
    BasketSerializer
)




class BasketProductsListApiView(APIView):
    """
    Представление для получения корзины, текущего юзера

    со всеми товарами\позициями
    """

    def get(self, request):
        basket = Basket.objects.filter(user=request.user)
        serializer = BasketSerializer(basket, many=True)
        return Response(serializer.data)

    def post(self):
        pass

    def destroy(self):
        pass


