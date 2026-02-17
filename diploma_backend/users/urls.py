from django.urls import path

from .views import (
    ProfileDetailView
)

urlpatterns = [
    path('profile/', ProfileDetailView.as_view(), name='current_profile_get'),
    path('profile', ProfileDetailView.as_view(), name='current_profile_post')
]