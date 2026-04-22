from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import (
    EmailAuthenticationForm,
    UserPasswordChangeForm,
    UserProfileForm,
    UserRegistrationForm,
)
from .models import User

PAGINATE_BY = 12

OWNERS_OF_FAVORITE_PROJECTS = "owners-of-favorite-projects"
OWNERS_OF_PARTICIPATING_PROJECTS = "owners-of-participating-projects"
INTERESTED_IN_MY_PROJECTS = "interested-in-my-projects"
PARTICIPANTS_OF_MY_PROJECTS = "participants-of-my-projects"

FILTER_CHOICES = (
    (OWNERS_OF_FAVORITE_PROJECTS, "Авторы избранных проектов"),
    (OWNERS_OF_PARTICIPATING_PROJECTS, "Авторы проектов, в которых я участвую"),
    (INTERESTED_IN_MY_PROJECTS, "Пользователи, которым нравятся мои проекты"),
    (PARTICIPANTS_OF_MY_PROJECTS, "Участники моих проектов"),
)


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "users/register.html"

    def get_success_url(self):
        return reverse("users:login")


class EmailLoginView(LoginView):
    form_class = EmailAuthenticationForm
    template_name = "users/login.html"

    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect("projects:list")


def logout_view(request):
    logout(request)
    return redirect("projects:list")


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = "users/change_password.html"

    def get_success_url(self):
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


class UserListView(ListView):
    model = User
    template_name = "users/participants.html"
    context_object_name = "participants"
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        queryset = User.objects.order_by("-date_joined").distinct()
        active_filter = self.request.GET.get("filter")

        if not self.request.user.is_authenticated or not active_filter:
            return queryset

        user = self.request.user

        if active_filter == OWNERS_OF_FAVORITE_PROJECTS:
            return (
                queryset.filter(owned_projects__interested_users=user)
                .exclude(pk=user.pk)
                .distinct()
            )

        if active_filter == OWNERS_OF_PARTICIPATING_PROJECTS:
            return (
                queryset.filter(owned_projects__participants=user)
                .exclude(pk=user.pk)
                .distinct()
            )

        if active_filter == INTERESTED_IN_MY_PROJECTS:
            return (
                queryset.filter(favorites__owner=user)
                .exclude(pk=user.pk)
                .distinct()
            )

        if active_filter == PARTICIPANTS_OF_MY_PROJECTS:
            return (
                queryset.filter(participated_projects__owner=user)
                .exclude(pk=user.pk)
                .distinct()
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_filter = self.request.GET.get("filter", "")
        context["filter_choices"] = FILTER_CHOICES
        context["active_filter"] = active_filter
        return context


class UserDetailView(DetailView):
    model = User
    template_name = "users/user-details.html"
    context_object_name = "user"

    def get_queryset(self):
        return User.objects.prefetch_related("owned_projects__participants")


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/edit_profile.html"
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})
