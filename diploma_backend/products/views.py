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
        .order_by('-date')[:16]
    )
    serializer_class = ProductSerializer

class ProductCategoryListView(ListAPIView):
    """
    Представление для получения категорий товаров
    """
    queryset = Category.objects.filter(is_active=True, parent=None)
    serializer_class = CategorySerializer

class ProductsPopularListView(ListAPIView):
    """
    Представление для получения популярных товаров
    """
    queryset = (
        Product
        .objects
        .filter(archived=False, is_limited=False, is_banner=False)
        .order_by("sort_index", "-purchases_count")[:8]
    )
    serializer_class = ProductSerializer

class ProductsBannersListView(ListAPIView):
    """
    Представление для получения банеров с товарами
    """
    queryset = (
        Product
        .objects
        .filter(is_limited=False, is_banner=True)
        .order_by('-date')[:3]
    )
    serializer_class = ProductSerializer