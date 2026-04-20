from django.core.paginator import Paginator
from django.views.generic import ListView

from .models import Project


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
