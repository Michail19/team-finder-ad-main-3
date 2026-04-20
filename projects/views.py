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


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project-details.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.select_related("owner").prefetch_related("participants")


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
            "is_favorite": is_favorite,
            "project_id": project.pk,
        }
    )
