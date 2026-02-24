from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ProductsLimitedListView,
    ProductCategoryListView,
    ProductsPopularListView,
    ProductsBannersListView,
    product_catalog, # функция представления, для обработки запроса catalog
    tags_popular, # функция представления, для обработки запроса GET /tags
    discounted_products, # функция представления, для обработки запроса GET /sale
    ProductDetailView, # представление для обработки запроса GET /product{id}
    ProductReviewCreateView, # представление обрабатывает запрос: создание отзыва
)


# router = DefaultRouter()
# router.register(r'limited', ProductsLimitedListView, basename="products_limited")


urlpatterns = [
    # *router.urls,
    path('products/limited/', ProductsLimitedListView.as_view(), name='products_limited'),
    path('categories/', ProductCategoryListView.as_view(), name='product_category'),
    path('products/popular/', ProductsPopularListView.as_view(), name='products_popular'),
    path('banners/', ProductsBannersListView.as_view(), name='products_banners'),
    path('catalog/', product_catalog, name='products_catalog'),
    path('tags/', tags_popular, name='tags_popular'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:id>/reviews', ProductReviewCreateView.as_view(), name='product_create_review'),
    path('sales', discounted_products, name='sales_products')
]