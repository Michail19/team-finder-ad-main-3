import re

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ProjectForm
from .models import Favorite, Project


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        return (
            Project.objects.select_related("owner")
            .prefetch_related("participants")
            .order_by("-created_at")
        )

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)

        if not self.request.user.is_authenticated:
            return response

        favorite_ids = Favorite.objects.filter(
            user=self.request.user
        ).values_list("project_id", flat=True)

        html = mark_favorite(response.rendered_content, favorite_ids)
        response.content = html.encode(response.charset)
        return response


class FavoriteProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "projects/favorite_projects.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        return (
            Project.objects.filter(favorites__user=self.request.user)
            .select_related("owner")
            .prefetch_related("participants")
            .order_by("-favorites__created_at")
            .distinct()
        )

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        project_ids = [project.pk for project in context["projects"]]
        html = mark_favorite(response.rendered_content, project_ids)
        response.content = html.encode(response.charset)
        return response


def mark_favorite(render_html, project_ids):
    html = render_html
    for project_id in project_ids:
        pattern = (
            rf'(<button[^>]*class="project-fav-icon )not-favorite("'
            rf'[^>]*data-project-id="{project_id}"[^>]*data-fav=")false(")'
        )
        replacement = r'\1favorite\2true\3'
        html = re.sub(pattern, replacement, html)
    return html


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project-details.html"
    context_object_name = "project"

    def get_queryset(self):
        return (
            Project.objects.select_related("owner")
            .prefetch_related("participants")
        )


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user

    def handle_no_permission(self):
        return HttpResponseForbidden("У вас нет доступа к этому действию.")


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
    project = get_object_or_404(Project, pk=pk)

    if project.owner != request.user:
        return JsonResponse({"status": "error", "message": "Нет доступа"}, status=403)

    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Метод не поддерживается"}, status=405)

    if project.status != Project.Status.CLOSED:
        project.status = Project.Status.CLOSED
        project.save(update_fields=["status"])

    return JsonResponse({
        "status": "ok",
        "project_status": project.status,
        "project_status_display": "Закрыт",
        "project_id": project.pk,
    })


@login_required
def toggle_favorite(request, pk):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Метод не поддерживается"},
            status=405,
        )

    project = get_object_or_404(Project, pk=pk)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        project=project,
    )

    if created:
        is_favorite = True
    else:
        favorite.delete()
        is_favorite = False

    return JsonResponse(
        {
            "status": "ok",
            "favorite": is_favorite,
            "project_id": project.pk,
        }
    )


@login_required
def toggle_participate(request, pk):
    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Метод не поддерживается"},
            status=405,
        )

    project = get_object_or_404(Project, pk=pk)

    if project.owner == request.user:
        return JsonResponse(
            {"status": "error", "message": "Автор проекта уже является участником"},
            status=400,
        )

    if project.status == Project.Status.CLOSED:
        return JsonResponse(
            {"status": "error", "message": "Нельзя участвовать в закрытом проекте"},
            status=400,
        )

    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True

    return JsonResponse(
        {
            "status": "ok",
            "participant": participant,
            "project_id": project.pk,
            "participants_count": project.participants.count(),
        }
    )
