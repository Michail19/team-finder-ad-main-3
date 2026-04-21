import io
import random

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont


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
                f"default_avatar_{self.email}.png",
                ContentFile(self._generate_avatar()),
                save=False,
            )
        super().save(*args, **kwargs)

    def _generate_avatar(self):
        size = (200, 200)
        background_colors = [
            "#5E81AC",
            "#6A8E7F",
            "#8F7A66",
            "#7B8FA1",
            "#8C7AA9",
            "#6D8299",
        ]
        bg_color = random.choice(background_colors)

        image = Image.new("RGB", size, bg_color)
        draw = ImageDraw.Draw(image)

        letter = (self.name[:1] or "U").upper()

        try:
            font = ImageFont.truetype("arial.ttf", 100)
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (size[0] - text_width) / 2
        y = (size[1] - text_height) / 2 - 10

        draw.text((x, y), letter, fill="white", font=font)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
