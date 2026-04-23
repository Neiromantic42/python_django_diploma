from django.urls import path

from .views import (  # представление для обработки запроса GET /product{id}; представление обрабатывает запрос: создание отзыва; функция представления, для обработки запроса GET /sale; функция представления, для обработки запроса catalog; функция представления, для обработки запроса GET /tags
    ProductCategoryListView, ProductDetailView, ProductReviewCreateView,
    ProductsBannersListView, ProductsLimitedListView, ProductsPopularListView,
    discounted_products, product_catalog, tags_popular)

urlpatterns = [
    path(
        "products/limited/", ProductsLimitedListView.as_view(), name="products_limited"
    ),
    path("categories/", ProductCategoryListView.as_view(), name="product_category"),
    path(
        "products/popular/", ProductsPopularListView.as_view(), name="products_popular"
    ),
    path("banners/", ProductsBannersListView.as_view(), name="products_banners"),
    path("catalog/", product_catalog, name="products_catalog"),
    path("tags/", tags_popular, name="tags_popular"),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path(
        "product/<int:id>/reviews",
        ProductReviewCreateView.as_view(),
        name="product_create_review",
    ),
    path("sales", discounted_products, name="sales_products"),
]
