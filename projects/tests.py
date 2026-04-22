from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.models import Project

User = get_user_model()


class ProjectTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="strongpassword123",
            name="Олег",
            surname="Владелец",
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            password="strongpassword123",
            name="Ирина",
            surname="Участник",
        )
        self.project = Project.objects.create(
            owner=self.owner,
            name="Demo Project",
            description="Описание проекта",
            status="open",
        )
        self.project.participants.add(self.owner)

    def test_project_list_page_is_available(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_create_project(self):
        self.client.login(email="owner@example.com", password="strongpassword123")

        response = self.client.post(
            reverse("projects:create-project"),
            data={
                "name": "New Project",
                "description": "Новый проект",
                "github_url": "https://github.com/example/new-project",
                "status": "open",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name="New Project").exists())

        project = Project.objects.get(name="New Project")
        self.assertEqual(project.owner, self.owner)
        self.assertTrue(project.participants.filter(pk=self.owner.pk).exists())

    def test_guest_cannot_create_project(self):
        response = self.client.get(reverse("projects:create-project"))
        self.assertEqual(response.status_code, 302)

    def test_only_owner_can_edit_project(self):
        self.client.login(email="other@example.com", password="strongpassword123")
        response = self.client.post(
            reverse("projects:edit", kwargs={"pk": self.project.pk}),
            data={
                "name": "Updated Name",
                "description": "Обновлено",
                "github_url": "https://github.com/example/demo-project",
                "status": "open",
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_owner_can_complete_project(self):
        self.client.login(email="owner@example.com", password="strongpassword123")
        response = self.client.post(
            reverse("projects:complete", kwargs={"pk": self.project.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, "closed")

    def test_user_can_toggle_favorite(self):
        self.client.login(email="other@example.com", password="strongpassword123")

        response = self.client.post(
            reverse("projects:toggle-favorite", kwargs={"pk": self.project.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.other.favorites.filter(pk=self.project.pk).exists())

    def test_user_can_toggle_participation(self):
        self.client.login(email="other@example.com", password="strongpassword123")

        response = self.client.post(
            reverse("projects:toggle-participate", kwargs={"pk": self.project.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.project.participants.filter(pk=self.other.pk).exists())
