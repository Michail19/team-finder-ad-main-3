from django.urls import path

from .views import (
    ProjectCreateView,
    ProjectDetailView,
    ProjectListView,
    ProjectUpdateView,
    complete_project,
)

app_name = "projects"

urlpatterns = [
    path("list/", ProjectListView.as_view(), name="list"),
    path("create-project/", ProjectCreateView.as_view(), name="create-project"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", ProjectUpdateView.as_view(), name="edit"),
    path("<int:pk>/complete/", complete_project, name="complete"),
]
