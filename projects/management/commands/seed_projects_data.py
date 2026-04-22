from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from projects.models import Project
from users.models import User

DEMO_PROJECTS = [
    {
        "owner_email": "ivanov@example.com",
        "name": "Task Tracker",
        "description": "Веб-приложение для управления личными и командными задачами.",
        "github_url": "https://github.com/ivanov-demo/task-tracker",
        "status": "open",
        "participant_emails": [
            "petrova@example.com",
            "sidorov@example.com",
        ],
        "favorite_by": [
            "petrova@example.com",
            "smirnova@example.com",
        ],
    },
    {
        "owner_email": "petrova@example.com",
        "name": "UI Kit Library",
        "description": "Библиотека UI-компонентов для веб-приложений.",
        "github_url": "https://github.com/petrova-demo/ui-kit-library",
        "status": "open",
        "participant_emails": [
            "ivanov@example.com",
            "smirnova@example.com",
        ],
        "favorite_by": [
            "ivanov@example.com",
            "kozlov@example.com",
        ],
    },
    {
        "owner_email": "sidorov@example.com",
        "name": "StudyHub",
        "description": "Платформа для совместного обучения и обмена материалами.",
        "github_url": "https://github.com/sidorov-demo/studyhub",
        "status": "open",
        "participant_emails": [
            "kozlov@example.com",
            "petrova@example.com",
        ],
        "favorite_by": [
            "ivanov@example.com",
            "smirnova@example.com",
        ],
    },
    {
        "owner_email": "smirnova@example.com",
        "name": "BugBoard",
        "description": "Сервис для баг-репортов, тест-кейсов и статусов проверки.",
        "github_url": "https://github.com/smirnova-demo/bugboard",
        "status": "closed",
        "participant_emails": [
            "ivanov@example.com",
        ],
        "favorite_by": [
            "sidorov@example.com",
        ],
    },
    {
        "owner_email": "kozlov@example.com",
        "name": "ML Notes",
        "description": "Мини-платформа для заметок и экспериментов по машинному обучению.",
        "github_url": "https://github.com/kozlov-demo/ml-notes",
        "status": "open",
        "participant_emails": [
            "sidorov@example.com",
            "smirnova@example.com",
        ],
        "favorite_by": [
            "petrova@example.com",
        ],
    },
]


class Command(BaseCommand):
    help = "Создаёт демонстрационные проекты, участников и избранное"

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep",
            action="store_true",
            help="Не удалять старые демо-проекты перед созданием новых",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        users_by_email = {
            user.email: user
            for user in User.objects.filter(
                email__in=self._all_emails_from_config()
            )
        }

        missing_emails = self._all_emails_from_config() - set(users_by_email.keys())
        if missing_emails:
            raise CommandError(
                "Не найдены пользователи для демо-проектов: "
                + ", ".join(sorted(missing_emails))
            )

        if not options["keep"]:
            self.stdout.write(self.style.WARNING("Удаление старых демо-проектов..."))
            Project.objects.filter(
                github_url__in=[item["github_url"] for item in DEMO_PROJECTS]
            ).delete()

        self.stdout.write(self.style.WARNING("Создание демо-проектов..."))

        for item in DEMO_PROJECTS:
            owner = users_by_email[item["owner_email"]]

            project, created = Project.objects.get_or_create(
                github_url=item["github_url"],
                defaults={
                    "owner": owner,
                    "name": item["name"],
                    "description": item["description"],
                    "status": item["status"],
                },
            )

            if not created:
                project.owner = owner
                project.name = item["name"]
                project.description = item["description"]
                project.status = item["status"]
                project.save()

            project.participants.clear()
            project.participants.add(owner)

            participant_users = [
                users_by_email[email]
                for email in item["participant_emails"]
                if email != owner.email
            ]
            if participant_users:
                project.participants.add(*participant_users)

            for user in users_by_email.values():
                user.favorites.remove(project)

            favorite_users = [users_by_email[email] for email in item["favorite_by"]]
            for user in favorite_users:
                user.favorites.add(project)

            self.stdout.write(
                self.style.SUCCESS(f"Готово: {project.name} ({project.owner.email})")
            )

        self.stdout.write(self.style.SUCCESS("Демо-проекты успешно созданы."))

    def _all_emails_from_config(self):
        emails = set()

        for item in DEMO_PROJECTS:
            emails.add(item["owner_email"])
            emails.update(item["participant_emails"])
            emails.update(item["favorite_by"])

        return emails
