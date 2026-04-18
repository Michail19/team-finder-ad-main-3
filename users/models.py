from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


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
        max_length=150,
    )
    surname = models.CharField(
        "фамилия",
        max_length=150,
    )
    avatar = models.ImageField(
        "аватар",
        upload_to="avatars/",
        blank=True,
        null=True,
    )
    about = models.TextField(
        "описание",
        blank=True,
    )
    email = models.EmailField(
        "email",
        unique=True,
    )
    phone = models.CharField(
        "телефон",
        max_length=32,
        blank=True,
    )
    github_url = models.URLField(
        "GitHub",
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.name} {self.surname}".strip() or self.email
