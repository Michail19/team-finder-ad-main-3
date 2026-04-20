from django.conf import settings
from django.db import models
from django.urls import reverse


class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Открыт"
        CLOSED = "closed", "Закрыт"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="автор",
    )
    name = models.CharField(
        "название",
        max_length=200,
    )
    description = models.TextField(
        "описание",
        blank=True,
    )
    github_url = models.URLField(
        "GitHub",
        blank=True,
    )
    status = models.CharField(
        "статус",
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participating_projects",
        blank=True,
        verbose_name="участники",
    )
    created_at = models.DateTimeField(
        "дата публикации",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "дата изменения",
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"pk": self.pk})


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="пользователь",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="проект",
    )
    created_at = models.DateTimeField(
        "дата добавления",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "project"],
                name="unique_user_favorite_project",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.project}"
