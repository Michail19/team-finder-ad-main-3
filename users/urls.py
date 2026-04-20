from django.urls import path

from .views import (
    EmailLoginView,
    RegisterView,
    UserDetailView,
    UserPasswordChangeView,
    UserUpdateView,
    logout_view,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", EmailLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("change-password/", UserPasswordChangeView.as_view(), name="change-password"),
    path("<int:pk>/", UserDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", UserUpdateView.as_view(), name="edit"),
]
