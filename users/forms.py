import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from .models import User


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )

    error_messages = {
        "invalid_login": "Неверный email или пароль.",
        "inactive": "Этот аккаунт неактивен.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(
                self.request,
                email=email,
                password=password,
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"]
                )
            if not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages["inactive"]
                )

        return cleaned_data

    def get_user(self):
        return self.user_cache


class UserPasswordChangeForm(PasswordChangeForm):
    pass


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "avatar",
            "name",
            "surname",
            "about",
            "phone",
            "github_url",
        )

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()

        uf = User.objects.filter(email=email)
        if self.instance.pk:
            uf = uf.exclude(pk=self.instance.pk)

        if uf.exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")

        return email

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()

        if phone and not re.fullmatch(r"(8\d{10}|\+7\d{10})", phone):
            raise forms.ValidationError(
                "Введите корректный номер телефона: 8XXXXXXXXXX или +7XXXXXXXXXX."
            )

        if not phone:
            return phone

        normalized_phone = "+7" + phone[1:] if phone.startswith("8") else phone

        uf = User.objects.filter(phone=normalized_phone)
        if self.instance.pk:
            uf = uf.exclude(pk=self.instance.pk)

        if uf.exists():
            raise forms.ValidationError("Номер телефона уже зарегистрирован.")

        return normalized_phone

    def clean_github_url(self):
        github_url = (self.cleaned_data.get("github_url") or "").strip()

        if not github_url:
            return github_url

        parsed = urlparse(github_url)
        domain = parsed.netloc.lower()

        allowed_domains = {"github.com", "www.github.com"}
        if domain not in allowed_domains:
            raise forms.ValidationError("Введите корректную ссылку на GitHub.")

        normalized_url = github_url.rstrip("/")

        uf = User.objects.filter(github_url=normalized_url)
        if self.instance.pk:
            uf = uf.exclude(pk=self.instance.pk)

        if uf.exists():
            raise forms.ValidationError(
                "Профиль пользователя с данной ссылкой на профиль GitHub уже существует."
            )

        return normalized_url
