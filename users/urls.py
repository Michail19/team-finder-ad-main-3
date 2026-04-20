from django.urls import path

from .views import (
    EmailLoginView,
    RegisterView,
    UserPasswordChangeView,
    logout_view,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", EmailLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("password-change/", UserPasswordChangeView.as_view(), name="password_change"),
]
