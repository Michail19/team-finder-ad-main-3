from django.urls import path

from .views import (
    FavoriteProjectListView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectListView,
    ProjectUpdateView,
    complete_project,
    toggle_favorite,
    toggle_participate,
)

app_name = "projects"

urlpatterns = [
    path("list/", ProjectListView.as_view(), name="list"),
    path("favorites/", FavoriteProjectListView.as_view(), name="favorites"),
    path("create-project/", ProjectCreateView.as_view(), name="create-project"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", ProjectUpdateView.as_view(), name="edit"),
    path("<int:pk>/complete/", complete_project, name="complete"),
    path("<int:pk>/toggle-favorite/", toggle_favorite, name="toggle-favorite"),
    path("<int:pk>/toggle-participate/", toggle_participate, name="toggle-participate"),
]
