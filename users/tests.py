from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserAuthTests(TestCase):
    def test_user_registration_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "name": "Иван",
                "surname": "Иванов",
                "email": "ivan@example.com",
                "password": "strongpassword123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("users:login"))
        self.assertTrue(User.objects.filter(email="ivan@example.com").exists())

    def test_login_with_email_works(self):
        user = User.objects.create_user(
            email="user@example.com",
            password="strongpassword123",
            name="Тест",
            surname="Пользователь",
        )

        response = self.client.post(
            reverse("users:login"),
            data={
                "email": "user@example.com",
                "password": "strongpassword123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("projects:list"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_edit_profile_requires_authentication(self):
        response = self.client.get(reverse("users:edit-profile"))
        self.assertEqual(response.status_code, 302)

    def test_avatar_is_generated_for_user_without_uploaded_avatar(self):
        user = User.objects.create_user(
            email="avatar@example.com",
            password="strongpassword123",
            name="Анна",
            surname="Петрова",
        )

        self.assertTrue(user.avatar)
        self.assertIn("default_avatar_", user.avatar.name)


class UserListTests(TestCase):
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

    def test_user_list_page_is_available(self):
        response = self.client.get(reverse("users:list"))
        self.assertEqual(response.status_code, 200)
