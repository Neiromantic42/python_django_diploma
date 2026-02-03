from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ProductsLimitedListView
)


# router = DefaultRouter()
# router.register(r'limited', ProductsLimitedListView, basename="products_limited")


urlpatterns = [
    # *router.urls,
    path('limited/', ProductsLimitedListView.as_view(), name="product_limited")
]