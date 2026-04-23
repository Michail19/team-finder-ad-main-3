from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.models import Project

User = get_user_model()

TEST_PASSWORD = "strongpassword123"

REGISTER_EMAIL = "ivan@example.com"
LOGIN_EMAIL = "user@example.com"
AVATAR_EMAIL = "avatar@example.com"

OWNER_EMAIL = "owner@example.com"
OTHER_EMAIL = "other@example.com"
THIRD_EMAIL = "third@example.com"

OWNERS_OF_FAVORITE_PROJECTS = "owners-of-favorite-projects"
OWNERS_OF_PARTICIPATING_PROJECTS = "owners-of-participating-projects"

FILTERED_PROJECT_NAME = "Filtered Project"
FILTERED_PROJECT_DESCRIPTION = "Описание"
OPEN_PROJECT_STATUS = "open"


class UserAuthTests(TestCase):
    def test_user_registration_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "name": "Иван",
                "surname": "Иванов",
                "email": REGISTER_EMAIL,
                "password": TEST_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("users:login"))
        self.assertTrue(User.objects.filter(email=REGISTER_EMAIL).exists())

    def test_login_with_email_works(self):
        user = User.objects.create_user(
            email=LOGIN_EMAIL,
            password=TEST_PASSWORD,
            name="Тест",
            surname="Пользователь",
        )

        response = self.client.post(
            reverse("users:login"),
            data={
                "email": LOGIN_EMAIL,
                "password": TEST_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("projects:list"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_edit_profile_requires_authentication(self):
        response = self.client.get(reverse("users:edit-profile"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_avatar_is_generated_for_user_without_uploaded_avatar(self):
        user = User.objects.create_user(
            email=AVATAR_EMAIL,
            password=TEST_PASSWORD,
            name="Анна",
            surname="Петрова",
        )

        self.assertTrue(user.avatar)
        self.assertIn("default_avatar_", user.avatar.name)


class UserListTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email=OWNER_EMAIL,
            password=TEST_PASSWORD,
            name="Олег",
            surname="Владелец",
        )
        self.other = User.objects.create_user(
            email=OTHER_EMAIL,
            password=TEST_PASSWORD,
            name="Ирина",
            surname="Участник",
        )
        self.third = User.objects.create_user(
            email=THIRD_EMAIL,
            password=TEST_PASSWORD,
            name="Сергей",
            surname="Автор",
        )

        self.project = Project.objects.create(
            owner=self.third,
            name=FILTERED_PROJECT_NAME,
            description=FILTERED_PROJECT_DESCRIPTION,
            status=OPEN_PROJECT_STATUS,
        )
        self.project.participants.add(self.third)

    def test_user_list_page_is_available(self):
        response = self.client.get(reverse("users:list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_filter_owners_of_favorite_projects_works(self):
        self.other.favorites.add(self.project)
        self.client.login(email=OTHER_EMAIL, password=TEST_PASSWORD)

        response = self.client.get(
            reverse("users:list"),
            data={"filter": OWNERS_OF_FAVORITE_PROJECTS},
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        participants = response.context["participants"]
        self.assertIn(self.third, participants)
        self.assertNotIn(self.other, participants)

    def test_filter_owners_of_participating_projects_works(self):
        self.project.participants.add(self.other)
        self.client.login(email=OTHER_EMAIL, password=TEST_PASSWORD)

        response = self.client.get(
            reverse("users:list"),
            data={"filter": OWNERS_OF_PARTICIPATING_PROJECTS},
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        participants = response.context["participants"]
        self.assertIn(self.third, participants)
        self.assertNotIn(self.other, participants)
