from django.urls import path

from .views import payment_create

urlpatterns = [path("payment/<int:id>", payment_create, name="payment-creation")]
