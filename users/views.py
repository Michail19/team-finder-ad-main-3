from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import (
    EmailAuthenticationForm,
    UserPasswordChangeForm,
    UserProfileForm,
    UserRegistrationForm,
)
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("projects:list")


class EmailLoginView(LoginView):
    form_class = EmailAuthenticationForm
    template_name = "users/login.html"

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect("projects:list")


def logout_view(request):
    logout(request)
    return redirect("users:login")


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = "users/change_password.html"
    success_url = reverse_lazy("projects:list")


class UserListView(ListView):
    model = User
    template_name = "users/participants.html"
    context_object_name = "participants"
    paginate_by = 12

    def get_queryset(self):
        queryset = User.objects.order_by("-date_joined").distinct()
        active_filter = self.request.GET.get("filter")

        if not self.request.user.is_authenticated or not active_filter:
            return queryset

        user = self.request.user

        if active_filter == "owners-of-favorite-projects":
            return (
                queryset.filter(
                    owned_projects__favorites__user=user
                )
                .exclude(pk=user.pk)
                .distinct()
            )

        if active_filter == "owners-of-participating-projects":
            return (
                queryset.filter(
                    owned_projects__participants=user
                )
                .exclude(pk=user.pk)
                .distinct()
            )

        if active_filter == "interested-in-my-projects":
            return (
                queryset.filter(
                    favorites__project__owner=user
                )
                .exclude(pk=user.pk)
                .distinct()
            )

        if active_filter == "participants-of-my-projects":
            return (
                queryset.filter(
                    participating_projects__owner=user
                )
                .exclude(pk=user.pk)
                .distinct()
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_filter"] = self.request.GET.get("filter", "")
        return context


class UserDetailView(DetailView):
    model = User
    template_name = "users/user-details.html"
    context_object_name = "user"

    def get_queryset(self):
        return User.objects.prefetch_related("owned_projects__participants")


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj == self.request.user

    def handle_no_permission(self):
        return HttpResponseForbidden("У вас нет доступа к этому действию.")


class UserUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/edit_profile.html"
    context_object_name = "user"

    def get_success_url(self):
        return reverse_lazy("users:detail", kwargs={"pk": self.object.pk})
