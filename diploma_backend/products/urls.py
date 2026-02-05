from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ProductsLimitedListView,
    ProductCategoryListView,
    ProductsPopularListView,
    ProductsBannersListView,

)


# router = DefaultRouter()
# router.register(r'limited', ProductsLimitedListView, basename="products_limited")


urlpatterns = [
    # *router.urls,
    path('products/limited/', ProductsLimitedListView.as_view(), name='product_limited'),
    path('categories/', ProductCategoryListView.as_view(), name='product_category'),
    path('products/popular/', ProductsPopularListView.as_view(), name='product_popular'),
    path('banners/', ProductsBannersListView.as_view(), name='product_banners'),
]