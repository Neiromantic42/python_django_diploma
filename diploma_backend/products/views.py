import logging
from rest_framework import status
from django.utils import timezone
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
from .models import Product, Category, Tag, Review, Sale
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    ProductDetailSerializer,
    ReviewSerializer,
    SalesSerializer,
)




logger = logging.getLogger(__name__) # Создаем логгер


class ProductDetailView(RetrieveAPIView):
    """
    представление на основе класса

    обрабатывает запрос на получение одного товара
    """
    queryset = (
        Product
        .objects
        .filter(archived=False)
        .select_related("category")
        .prefetch_related('specifications', 'images', 'reviews', 'tags')
        .annotate( # Добавляем в qs вычисляемые поля:
            avg_rating = Avg('reviews__rate') # Средний рейтинг
        )
    )
    serializer_class = ProductDetailSerializer


class ProductsLimitedListView(ListAPIView):
    """
    Представление для получения списка лимитированных товаров.
    """
    queryset = (
        Product
        .objects
        .filter(is_limited=True, archived=False, count__gt=0)
        .order_by('-date')
        .select_related("sale", "category")
        .prefetch_related('tags', 'images', "reviews")
        .annotate( # Добавляем в qs вычисляемые поля:
            reviews_count = Count("reviews"), # Кол-во отзывов
            avg_rating = Avg("reviews__rate") # Средний рейтинг
        )
    )[:16]
    serializer_class = ProductSerializer


class ProductCategoryListView(ListAPIView):
    """
    Представление для получения категорий товаров
    """
    queryset = (
        Category
        .objects
        .filter(is_active=True, parent=None)
        .select_related("image") # В одном запросе загружаем связанные картинки
        .prefetch_related(
            Prefetch(
                'subcategories',
                queryset=Category.objects.filter(is_active=True)
            )
        )
    )
    serializer_class = CategorySerializer


class ProductsPopularListView(ListAPIView):
    """
    Представление для получения популярных товаров
    """
    queryset = (
        Product
        .objects
        .filter(archived=False, is_limited=False, is_banner=False)
        .order_by("sort_index", "-purchases_count")
        .annotate( # Добавляем в qs вычисляемые поля:
            reviews_count = Count("reviews"), # Кол-во отзывов
            avg_rating = Avg("reviews__rate") # Средний рейтинг
        )
    )[:8]
    serializer_class = ProductSerializer


class ProductsBannersListView(ListAPIView):
    """
    Представление для получения банеров с товарами
    """
    queryset = (
        Product
        .objects
        .filter(is_limited=False, is_banner=True)
        .order_by('-date')
        .annotate(  # Добавляем в qs вычисляемые поля:
            reviews_count=Count("reviews"),  # Кол-во отзывов
            avg_rating=Avg("reviews__rate")  # Средний рейтинг
        )
    )[:3]
    serializer_class = ProductSerializer


@api_view(["GET"])
def product_catalog(request):
    """
    Представление на основе функции, обслуживает страницу catalog
    """
    # получаем все доступные продукты
    products = (
        Product
        .objects
        .filter(archived=False)
        .select_related("sale", "category")
        .prefetch_related('tags', 'images')
        .annotate(  # Добавляем в qs вычисляемые поля:
            reviews_count=Count("reviews"),  # Кол-во отзывов
            avg_rating=Coalesce(Avg("reviews__rate"), 0.0)  # Средний рейтинг
        )
    )

    # получаем все фильтры из строки запроса
    filter_name = request.GET.get('filter[name]', '')
    filter_min_price = float(request.GET.get('filter[minPrice]', 0))
    filter_max_price = float(request.GET.get('filter[maxPrice]', 50000))
    filter_available = request.GET.get('filter[available]')
    filter_free_delivery = request.GET.get('filter[freeDelivery]')
    filter_tags = request.GET.getlist('tags[]')
    category_filter = request.GET.get('category')
    # получаем все сортировки из строки запроса
    sort = request.GET.get('sort')
    sort_type = request.GET.get('sortType')

    # логируем данные по фильтрации и сортировкам из запроса
    logger.info(
        f"Параметры фильтрации и сортировки запроса:\n"
        f"  - Фильтр по имени товара: {filter_name}\n"
        f"  - Фильтр по минимальной цене: {filter_min_price}\n"
        f"  - Фильтр по максимальной цене: {filter_max_price}\n"
        f"  - Только товары в наличии: {filter_available}\n"
        f"  - Бесплатная доставка: {filter_free_delivery}\n"
        f"  - Фильтр по категории: {category_filter}\n"
        f"  - Сортировка по: {sort}\n"
        f"  - Тип сортировки: {sort_type}\n"
        f"  - Массив тегов: {filter_tags}"
    )

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
    # проверяем, пришел ли в строке запроса массив с тегами ['1', '2']
    if filter_tags:
        products = products.filter(tags__pk__in=filter_tags).distinct()
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
        # products = products.annotate(review_count=Count('reviews'))
        products = products.order_by('-reviews_count')
    elif sort=='reviews' and sort_type=='inc':
        # products = products.annotate(review_count=Count('reviews'))
        products = products.order_by('reviews_count')
    elif sort=='date' and sort_type=='inc':
        products = products.order_by('date')
    elif sort=='date' and sort_type=='dec':
        products = products.order_by('-date')
    # сортировка по рейтингу
    elif sort=='rating':
        # products = products.annotate(
        #     avg_rating=Coalesce(Avg('reviews__rate'), 0.0))
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


@api_view(["GET"])
def tags_popular(request):
    """
    представление на основе функции

    обрабатывает запрос GET tags/
    отдает теги товаров
    """
    category = request.GET.get('category', None)

    if category:
        # получаем все товары относящиеся к переданной категории
        products = Product.objects.filter(category_id=category)
        # получаем все теги от продуктов с переданной категорией
        tags = Tag.objects.filter(products__in=products).distinct()
        return Response([
            {
                "id": tag.pk,
                "name": tag.name
            }
            for tag in tags
        ])

    tags = Tag.objects.all()

    return Response([
        {
            "id": tag.pk,
            "name": tag.name
        }
        for tag in tags
    ])


@api_view(["GET"])
def discounted_products(request):
    """
    Представление на основе функции, обслуживает страницу товаров со скидкой

    GET /sales
    """
    current_data = timezone.now().date()
    # получаем все активные скидки\акции Sale
    queryset = Sale.objects.filter(date_from__lte=current_data, date_to__gte=current_data)
    # получаем текущую страницу
    current_page = int(request.GET.get('currentPage', 1))
    # лимит товаров на 1 странице
    limit = 10

    paginator = Paginator(queryset, limit) # В пагинатор передаем qs и лимит страниц
    last_page = paginator.num_pages # вычисляем последнюю страницу
    sale_page = paginator.get_page(current_page) # получаем только товары с переданной в запросе страницы

    # В сериализатор передаем обьекты Sale (акции с товарами по скидке)
    serializer = SalesSerializer(sale_page, many=True)

    return Response({
        "items":serializer.data,
        "currentPage": current_page,
        "lastPage": last_page
    })




class ProductReviewCreateView(CreateAPIView):
    """
    представление на основе класса CreateAPIView

    Обеспечивает создание отзыва о конкретном товаре
    """
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        """
        переопределяем родительский метод perform_create

        он сохранит и вернет отзыв о конкретном товаре
        """
        product_pk = self.kwargs['id']
        queryset = Product.objects
        product = get_object_or_404(queryset, id=product_pk)
        serializer.save(product=product)

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        product_pk = self.kwargs['id']
        reviews = Review.objects.filter(product=product_pk)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
