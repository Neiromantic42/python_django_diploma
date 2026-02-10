import logging
from django.db.models.functions import Coalesce
from rest_framework.viewsets import ModelViewSet
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models import  Avg
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


logger = logging.getLogger(__name__) # Создаем логгер


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


@api_view(["GET"])
def product_catalog(request):
    """
    Представление на основе функции, обслуживает страницу catalog
    """
    # получаем все доступные продукты
    products = Product.objects.filter(archived=False)

    # получаем все фильтры из строки запроса
    filter_name = request.GET.get('filter[name]', '')
    filter_min_price = float(request.GET.get('filter[minPrice]', 0))
    filter_max_price = float(request.GET.get('filter[maxPrice]', 50000))
    filter_available = request.GET.get('filter[available]')
    filter_free_delivery = request.GET.get('filter[freeDelivery]')
    category_filter = request.GET.get('category')
    # получаем все сортировки из строки запроса
    sort = request.GET.get('sort')
    sort_type = request.GET.get('sortType')

    # логируем данные по фильтрации и сортировкам из запроса
    logger.info(f"Фильтр по имени товара: {filter_name},"
                 f"\nФильтр по минимальной цене: {filter_min_price},"
                 f"\nФильтр по максимальной цене:{filter_max_price},"
                 f"\nФильтр кол-ва товара, больше нуля: {filter_available},"
                 f"\nФильтр бесплатной доставки: {filter_free_delivery},"
                 f"\nФильтр по категории: {category_filter},"
                 f"\nСортировка по: {sort},"
                 f"\nТип сортировки: {sort_type}")

    # проверяем, пришел ли в строке запроса фильтр, имени товара
    if filter_name:
        # поиск по имени продукта, накапливаем в qs условия фильтрации
        products = products.filter(title__icontains=filter_name)
    # проверяем что minPrice не равно 0, значение фильтра передано!
    if filter_min_price != 0:
        # применяя фильтр >= minPrice, накапливаем в qs условия фильтрации
        products = products.filter(price__gte=filter_min_price)
    # проверяем что maxPrice передано и применяем фильтр
    if filter_max_price != 50000:
        # применяя фильтр <= maxPrice, накапливаем в qs условия фильтрации
        products = products.filter(price__lte=filter_max_price)
    # проверяем, пришел ли в строке запроса фильтр, наличия товара
    if filter_available == 'true':
        # применяя фильтр available=True, накапливаем в qs условия фильтрации
        products = products.filter(count__gt=0)
    # проверяем, пришел ли в строке запроса фильтр, бесплатная доставка
    if filter_free_delivery == 'true':
        # применяя фильтр freeDelivery=True, накапливаем в qs условия фильтрации
        products = products.filter(free_delivery=True)
    # проверяем, пришел ли в строке запроса фильтр, category
    if category_filter:
        # применяя фильтр category, накапливаем в qs условия фильтрации
        products = products.filter(category=category_filter)

    # применяем сортировки
    if sort=='price' and sort_type=='inc':
        # если сортировка по цене, от меньшего к большему
        products = products.order_by('price')
    elif sort=='price' and sort_type=='dec':
        products = products.order_by('-price')
    elif sort=='reviews' and sort_type=='dec':
        products = products.annotate(review_count=Count('reviews'))
        products = products.order_by('-review_count')
    elif sort=='reviews' and sort_type=='inc':
        products = products.annotate(review_count=Count('reviews'))
        products = products.order_by('review_count')
    elif sort=='date' and sort_type=='inc':
        products = products.order_by('date')
    elif sort=='date' and sort_type=='dec':
        products = products.order_by('-date')
    # сортировка по рейтингу
    elif sort=='rating':
        products = products.annotate(
            avg_rating=Coalesce(Avg('reviews__rate'), 0.0))
        if sort_type=='dec':
            # по убыванию среднего рейтинга
            products = products.order_by('-avg_rating')
        else:
            # по возрастанию среднего рейтинга
            products = products.order_by('avg_rating')

    # пагинация
    limit = int(request.GET.get('limit', 20)) # получаем кол-во товаров на странице
    current_page = int(request.GET.get('currentPage', 1)) # получаем текущую страницу

    paginator = Paginator(products, limit) # В пагинатор передаем qs и лимит страниц
    products_page = paginator.get_page(current_page) # получаем только товары с переданной в запросе страницы

    # В сериализатор передаем обьекты продуктов с пагинацией
    serializer = ProductSerializer(products_page, many=True)

    return Response({
        "items": serializer.data,
        "currentPage": current_page,
        "lastPage": paginator.num_pages
    })