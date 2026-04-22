from urllib.parse import urlparse

from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")

    def clean_github_url(self):
        github_url = (self.cleaned_data.get("github_url") or "").strip()

        if not github_url:
            return github_url

        parsed = urlparse(github_url)
        domain = parsed.netloc.lower()

        if domain not in {"github.com", "www.github.com"}:
            raise forms.ValidationError("Введите корректную ссылку на GitHub.")

        normalized_url = github_url.rstrip("/")

        pf = Project.objects.filter(github_url=normalized_url)
        if self.instance.pk:
            pf = pf.exclude(pk=self.instance.pk)

        if pf.exists():
            raise forms.ValidationError("Профиль пользователя с данной ссылкой на профиль GitHub"
                                        " уже существует.")

        return normalized_url
