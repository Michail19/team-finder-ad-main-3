from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.models import Project, ProjectStatus

User = get_user_model()

TEST_PASSWORD = "strongpassword123"

OWNER_EMAIL = "owner@example.com"
OTHER_EMAIL = "other@example.com"

OWNER_NAME = "Олег"
OWNER_SURNAME = "Владелец"
OTHER_NAME = "Ирина"
OTHER_SURNAME = "Участник"

DEMO_PROJECT_NAME = "Demo Project"
DEMO_PROJECT_DESCRIPTION = "Описание проекта"
NEW_PROJECT_NAME = "New Project"
NEW_PROJECT_DESCRIPTION = "Новый проект"
UPDATED_PROJECT_NAME = "Updated Name"
UPDATED_PROJECT_DESCRIPTION = "Обновлено"
OTHER_PROJECT_NAME = "Other Project"
OTHER_PROJECT_DESCRIPTION = "Описание другого проекта"

NEW_PROJECT_GITHUB_URL = "https://github.com/example/new-project"
UPDATED_PROJECT_GITHUB_URL = "https://github.com/example/demo-project"


class ProjectTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email=OWNER_EMAIL,
            password=TEST_PASSWORD,
            name=OWNER_NAME,
            surname=OWNER_SURNAME,
        )
        self.other = User.objects.create_user(
            email=OTHER_EMAIL,
            password=TEST_PASSWORD,
            name=OTHER_NAME,
            surname=OTHER_SURNAME,
        )
        self.project = Project.objects.create(
            owner=self.owner,
            name=DEMO_PROJECT_NAME,
            description=DEMO_PROJECT_DESCRIPTION,
            status=ProjectStatus.OPEN,
        )
        self.project.participants.add(self.owner)

    def test_project_list_page_is_available(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user_can_create_project(self):
        self.client.login(email=OWNER_EMAIL, password=TEST_PASSWORD)

        response = self.client.post(
            reverse("projects:create-project"),
            data={
                "name": NEW_PROJECT_NAME,
                "description": NEW_PROJECT_DESCRIPTION,
                "github_url": NEW_PROJECT_GITHUB_URL,
                "status": ProjectStatus.OPEN,
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Project.objects.filter(name=NEW_PROJECT_NAME).exists())

        project = Project.objects.get(name=NEW_PROJECT_NAME)
        self.assertEqual(project.owner, self.owner)
        self.assertTrue(project.participants.filter(pk=self.owner.pk).exists())

    def test_guest_cannot_create_project(self):
        response = self.client.get(reverse("projects:create-project"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_only_owner_can_edit_project(self):
        self.client.login(email=OTHER_EMAIL, password=TEST_PASSWORD)

        response = self.client.post(
            reverse("projects:edit", kwargs={"pk": self.project.pk}),
            data={
                "name": UPDATED_PROJECT_NAME,
                "description": UPDATED_PROJECT_DESCRIPTION,
                "github_url": UPDATED_PROJECT_GITHUB_URL,
                "status": ProjectStatus.OPEN,
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_owner_can_complete_project(self):
        self.client.login(email=OWNER_EMAIL, password=TEST_PASSWORD)

        response = self.client.post(
            reverse("projects:complete", kwargs={"pk": self.project.pk})
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, ProjectStatus.CLOSED)

    def test_user_can_toggle_favorite(self):
        self.client.login(email=OTHER_EMAIL, password=TEST_PASSWORD)

        response = self.client.post(
            reverse("projects:toggle-favorite", kwargs={"pk": self.project.pk})
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(self.other.favorites.filter(pk=self.project.pk).exists())

    def test_user_can_toggle_participation(self):
        self.client.login(email=OTHER_EMAIL, password=TEST_PASSWORD)

        response = self.client.post(
            reverse("projects:toggle-participate", kwargs={"pk": self.project.pk})
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(self.project.participants.filter(pk=self.other.pk).exists())

    def test_favorite_projects_page_shows_only_user_favorites(self):
        other_project = Project.objects.create(
            owner=self.other,
            name=OTHER_PROJECT_NAME,
            description=OTHER_PROJECT_DESCRIPTION,
            status=ProjectStatus.OPEN,
        )
        other_project.participants.add(self.other)

        self.other.favorites.add(self.project)
        self.client.login(email=OTHER_EMAIL, password=TEST_PASSWORD)

        response = self.client.get(reverse("projects:favorites"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        projects = response.context["projects"]
        self.assertIn(self.project, projects)
        self.assertNotIn(other_project, projects)
