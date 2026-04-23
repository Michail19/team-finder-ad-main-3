from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ProjectForm
from .mixins import OwnerRequiredMixin
from .models import Project, ProjectStatus

PAGINATE_BY = 12
ERROR_STATUS = "error"
OK_STATUS = "ok"
METHOD_NOT_ALLOWED_MESSAGE = "Метод не поддерживается"
ACCESS_DENIED_MESSAGE = "Нет доступа"
PROJECT_ALREADY_CLOSED_MESSAGE = "Проект уже закрыт"


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return (
            Project.objects.select_related("owner")
            .prefetch_related("participants")
            .order_by("-created_at")
        )


class FavoriteProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "projects/favorite_projects.html"
    context_object_name = "projects"
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return (
            self.request.user.favorites.select_related("owner")
            .prefetch_related("participants")
            .order_by("-created_at")
        )


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project-details.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.select_related("owner").prefetch_related("participants")


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        self.object.participants.add(self.request.user)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = False
        return context


class ProjectUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context


@login_required
def complete_project(request, pk):
    if request.method != "POST":
        return JsonResponse(
            {"status": ERROR_STATUS, "message": METHOD_NOT_ALLOWED_MESSAGE},
            status=HTTPStatus.METHOD_NOT_ALLOWED,
        )

    project = get_object_or_404(Project, pk=pk)

    if project.owner != request.user:
        return JsonResponse(
            {"status": ERROR_STATUS, "message": ACCESS_DENIED_MESSAGE},
            status=HTTPStatus.FORBIDDEN,
        )

    if project.status != ProjectStatus.OPEN:
        return JsonResponse(
            {"status": ERROR_STATUS, "message": PROJECT_ALREADY_CLOSED_MESSAGE},
            status=HTTPStatus.BAD_REQUEST,
        )

    project.status = ProjectStatus.CLOSED
    project.save(update_fields=["status"])

    return JsonResponse(
        {"status": OK_STATUS, "project_status": ProjectStatus.CLOSED},
        status=HTTPStatus.OK,
    )


@login_required
def toggle_favorite(request, pk):
    if request.method != "POST":
        return JsonResponse(
            {"status": ERROR_STATUS, "message": METHOD_NOT_ALLOWED_MESSAGE},
            status=HTTPStatus.METHOD_NOT_ALLOWED,
        )

    project = get_object_or_404(Project, pk=pk)

    if request.user.favorites.filter(pk=project.pk).exists():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True

    return JsonResponse(
        {"status": OK_STATUS, "favorited": favorited},
        status=HTTPStatus.OK,
    )


@login_required
def toggle_participate(request, pk):
    if request.method != "POST":
        return JsonResponse(
            {"status": ERROR_STATUS, "message": METHOD_NOT_ALLOWED_MESSAGE},
            status=HTTPStatus.METHOD_NOT_ALLOWED,
        )

    project = get_object_or_404(Project, pk=pk)

    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True

    return JsonResponse(
        {"status": OK_STATUS, "participant": participant},
        status=HTTPStatus.OK,
    )
