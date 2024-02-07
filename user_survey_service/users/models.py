from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    """
    Кастомная модель переопределенного юзера.
    При создании пользователя все поля обязательны для заполнения.
    """
    class RoleChoises(models.TextChoices):
        """
        Определение роли юзера.
        """
        USER = "user"
        ADMIN = "admin"

    # REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name="email address",
    )
    username = models.CharField(
        "Логин пользователя",
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(
        "Имя пользователя",
        max_length=255,
    )
    last_name = models.CharField(
        "Фамилия пользователя",
        max_length=255,
    )
    password = models.CharField(
        "Пароль пользователя",
        max_length=255,
    )
    role = models.TextField(
        "Пользовательская роль юзера",
        choices=RoleChoises.choices,
        default=RoleChoises.USER,
        max_length=255,
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-id"]

    def __str__(self):
        return str(self.username)