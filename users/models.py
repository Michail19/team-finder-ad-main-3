from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db import models

from .utils import DEFAULT_AVATAR_FILENAME_TEMPLATE, generate_avatar


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Поле email должно быть заполнено.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None

    name = models.CharField(
        "имя",
        max_length=124,
    )
    surname = models.CharField(
        "фамилия",
        max_length=124,
    )
    avatar = models.ImageField(
        "аватар",
        upload_to="avatars/",
        blank=True,
    )
    phone = models.CharField(
        "телефон",
        max_length=12,
        blank=True,
    )
    github_url = models.URLField(
        "GitHub",
        blank=True,
    )
    about = models.TextField(
        "описание",
        blank=True,
        max_length=256,
    )
    email = models.EmailField(
        "email",
        unique=True,
    )

    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="избранные проекты",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.name} {self.surname}".strip() or self.email

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar.save(
                DEFAULT_AVATAR_FILENAME_TEMPLATE.format(email=self.email),
                ContentFile(generate_avatar(self.name)),
                save=False,
            )
        super().save(*args, **kwargs)
