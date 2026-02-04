import logging
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer



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

class ProductCategory(ListAPIView):
    """
    Представление для получения категорий товаров
    """
    queryset = Category.objects.filter(is_active=True, parent=None)
    serializer_class = CategorySerializer

