from django.urls import path

from .views import (
    RegisterView,
    UserPasswordChangeView,
    login_view,
    logout_view,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("password-change/", UserPasswordChangeView.as_view(), name="password_change"),
]
