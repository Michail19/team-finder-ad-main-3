from django.conf import settings
from django.db import models
from django.urls import reverse


class ProjectStatus(models.TextChoices):
    OPEN = "open", "Открыт"
    CLOSED = "closed", "Закрыт"


class Project(models.Model):
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
        max_length=6,
        choices=ProjectStatus.choices,
        default=ProjectStatus.OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="участники",
    )
    created_at = models.DateTimeField(
        "дата публикации",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"pk": self.pk})
