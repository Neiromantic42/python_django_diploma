import logging
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from .models import Product
from .serializers import ProductSerializer



log = logging.getLogger(__name__) # Создаем логгер



class ProductsLimitedListView(ListAPIView):
    """
    Представление для получения списка лимитированных товаров.
    """
    queryset = (
        Product
        .objects
        .filter(is_limited=True, archived=False)
        .order_by('-date')[:8]
    )
    serializer_class = ProductSerializer


