from django.urls import path

from .views import (AvatarUpdateApiView, PasswordUpdateApiView,
                    ProfileDetailView)

urlpatterns = [
    path("profile/", ProfileDetailView.as_view(), name="current_profile_get"),
    path("profile", ProfileDetailView.as_view(), name="current_profile_post"),
    path("profile/avatar", AvatarUpdateApiView.as_view(), name="current_avatar_update"),
    path(
        "profile/password",
        PasswordUpdateApiView.as_view(),
        name="current_password_update",
    ),
]
