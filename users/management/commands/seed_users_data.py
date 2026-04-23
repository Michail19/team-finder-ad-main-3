from django.core.management.base import BaseCommand
from django.db import transaction

from projects.models import Project
from users.models import User

DEMO_USERS = [
    {
        "email": "ivanov@example.com",
        "password": "teamfinder123",
        "name": "Иван",
        "surname": "Иванов",
        "phone": "+79001000001",
        "github_url": "https://github.com/ivanov-demo",
        "about": "Backend-разработчик, интересуюсь Django и PostgreSQL.",
    },
    {
        "email": "petrova@example.com",
        "password": "teamfinder123",
        "name": "Анна",
        "surname": "Петрова",
        "phone": "+79001000002",
        "github_url": "https://github.com/petrova-demo",
        "about": "Frontend-разработчик, работаю с React и UI/UX.",
    },
    {
        "email": "sidorov@example.com",
        "password": "teamfinder123",
        "name": "Максим",
        "surname": "Сидоров",
        "phone": "+79001000003",
        "github_url": "https://github.com/sidorov-demo",
        "about": "Fullstack-разработчик, люблю собирать MVP.",
    },
    {
        "email": "smirnova@example.com",
        "password": "teamfinder123",
        "name": "Елена",
        "surname": "Смирнова",
        "phone": "+79001000004",
        "github_url": "https://github.com/smirnova-demo",
        "about": "QA-инженер и аналитик, люблю порядок в проектах.",
    },
    {
        "email": "kozlov@example.com",
        "password": "teamfinder123",
        "name": "Дмитрий",
        "surname": "Козлов",
        "phone": "+79001000005",
        "github_url": "https://github.com/kozlov-demo",
        "about": "Python-разработчик, интересуюсь ML и автоматизацией.",
    },
]


DEMO_PROJECTS = [
    {
        "owner_email": "ivanov@example.com",
        "name": "Task Tracker",
        "description": "Веб-приложение для управления личными и командными задачами.",
        "github_url": "https://github.com/ivanov-demo/task-tracker",
        "status": "open",
    },
    {
        "owner_email": "petrova@example.com",
        "name": "UI Kit Library",
        "description": "Библиотека переиспользуемых UI-компонентов для веб-проектов.",
        "github_url": "https://github.com/petrova-demo/ui-kit-library",
        "status": "open",
    },
    {
        "owner_email": "sidorov@example.com",
        "name": "StudyHub",
        "description": "Платформа для совместного обучения и обмена учебными материалами.",
        "github_url": "https://github.com/sidorov-demo/studyhub",
        "status": "open",
    },
    {
        "owner_email": "smirnova@example.com",
        "name": "BugBoard",
        "description": "Сервис для учёта багов, тест-кейсов и статусов проверки.",
        "github_url": "https://github.com/smirnova-demo/bugboard",
        "status": "closed",
    },
    {
        "owner_email": "kozlov@example.com",
        "name": "ML Notes",
        "description": "Мини-платформа для хранения заметок и экспериментов по ML.",
        "github_url": "https://github.com/kozlov-demo/ml-notes",
        "status": "open",
    },
]


class Command(BaseCommand):
    help = "Создаёт демонстрационные данные для ревьюера"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Удаление старых демоданных..."))
        self._cleanup_demo_data()

        self.stdout.write(self.style.WARNING("Создание пользователей..."))
        users_by_email = self._create_users()

        self.stdout.write(self.style.WARNING("Создание проектов..."))
        projects_by_name = self._create_projects(users_by_email)

        self.stdout.write(self.style.WARNING("Создание участников..."))
        self._assign_participants(users_by_email, projects_by_name)

        self.stdout.write(self.style.WARNING("Создание избранного..."))
        self._assign_favorites(users_by_email, projects_by_name)

        self.stdout.write(self.style.SUCCESS("Демоданные успешно созданы."))
        self.stdout.write("")
        self.stdout.write("Тестовые пользователи:")
        for user_data in DEMO_USERS:
            self.stdout.write(
                f"- {user_data['email']} / {user_data['password']}"
            )

    def _cleanup_demo_data(self):
        demo_emails = [item["email"] for item in DEMO_USERS]
        Project.objects.filter(owner__email__in=demo_emails).delete()
        User.objects.filter(email__in=demo_emails).delete()

    def _create_users(self):
        result = {}

        for user_data in DEMO_USERS:
            user = User.objects.create_user(
                email=user_data["email"],
                password=user_data["password"],
                name=user_data["name"],
                surname=user_data["surname"],
                phone=user_data["phone"],
                github_url=user_data["github_url"],
                about=user_data["about"],
            )
            result[user.email] = user

        return result

    def _create_projects(self, users_by_email):
        result = {}

        for project_data in DEMO_PROJECTS:
            owner = users_by_email[project_data["owner_email"]]
            project = Project.objects.create(
                owner=owner,
                name=project_data["name"],
                description=project_data["description"],
                github_url=project_data["github_url"],
                status=project_data["status"],
            )
            project.participants.add(owner)
            result[project.name] = project

        return result

    def _assign_participants(self, users_by_email, projects_by_name):
        projects_by_name["Task Tracker"].participants.add(
            users_by_email["petrova@example.com"],
            users_by_email["sidorov@example.com"],
        )
        projects_by_name["UI Kit Library"].participants.add(
            users_by_email["ivanov@example.com"],
            users_by_email["smirnova@example.com"],
        )
        projects_by_name["StudyHub"].participants.add(
            users_by_email["kozlov@example.com"],
            users_by_email["petrova@example.com"],
        )
        projects_by_name["BugBoard"].participants.add(
            users_by_email["ivanov@example.com"],
        )
        projects_by_name["ML Notes"].participants.add(
            users_by_email["sidorov@example.com"],
            users_by_email["smirnova@example.com"],
        )

    def _assign_favorites(self, users_by_email, projects_by_name):
        users_by_email["ivanov@example.com"].favorites.add(
            projects_by_name["UI Kit Library"],
            projects_by_name["StudyHub"],
        )
        users_by_email["petrova@example.com"].favorites.add(
            projects_by_name["Task Tracker"],
            projects_by_name["ML Notes"],
        )
        users_by_email["sidorov@example.com"].favorites.add(
            projects_by_name["Task Tracker"],
            projects_by_name["BugBoard"],
        )
        users_by_email["smirnova@example.com"].favorites.add(
            projects_by_name["StudyHub"],
        )
        users_by_email["kozlov@example.com"].favorites.add(
            projects_by_name["UI Kit Library"],
            projects_by_name["Task Tracker"],
        )
