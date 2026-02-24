from django.urls import path
from .views import (
    BasketProductsListApiView,

)


urlpatterns = [
    path('basket/',BasketProductsListApiView.as_view(), name="get_basket"),
    path('basket', BasketProductsListApiView.as_view(), name="post_basket")
]