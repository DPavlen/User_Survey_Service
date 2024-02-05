from django.contrib import admin

from .models import MyUser


class BaseAdminSettings(admin.ModelAdmin):
    """Базовая настроенная админ панели."""

    empty_value_display = "-пусто-"
    list_filter = ("email", "username")


@admin.register(MyUser)
class UsersAdmin(BaseAdminSettings):
    """Настроенная панель админки (управление пользователями)."""

    list_display = (
        "id",
        "role",
        "username",
        "email",
        "first_name",
        "last_name"
    )
    list_display_links = ("id", "username")
    search_fields = ("username", "role")