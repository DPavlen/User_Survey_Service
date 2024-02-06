# Generated by Django 4.2 on 2024-02-06 10:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Survey",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=255, unique=True, verbose_name="Опрос"),
                ),
                (
                    "description",
                    models.CharField(
                        max_length=255, verbose_name="Полное описание опроса"
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        max_length=155,
                        unique=True,
                        verbose_name="Уникальный слаг опроса",
                    ),
                ),
            ],
            options={
                "verbose_name": "Опрос",
                "verbose_name_plural": "Опросы",
            },
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        max_length=255, unique=True, verbose_name="Вопрос"
                    ),
                ),
                ("text", models.TextField()),
                (
                    "survey",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="questions",
                        to="surveys.survey",
                        verbose_name="Опрос",
                    ),
                ),
            ],
            options={
                "verbose_name": "Вопрос",
                "verbose_name_plural": "Вопросы",
            },
        ),
        migrations.CreateModel(
            name="Choice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "text",
                    models.CharField(
                        max_length=255, verbose_name="Текст варианта ответа"
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="choices",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор выбранного ответа",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="choices",
                        to="surveys.question",
                        verbose_name="Выбор",
                    ),
                ),
                (
                    "survey",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="choices",
                        to="surveys.survey",
                        verbose_name="Опрос",
                    ),
                ),
            ],
            options={
                "verbose_name": "Выбор варианта ответа",
                "verbose_name_plural": "Выбор вариантов ответов",
            },
        ),
        migrations.CreateModel(
            name="Answer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Ответ")),
                ("text", models.TextField()),
                (
                    "pub_date",
                    models.DateTimeField(auto_now_add=True, verbose_name="Дата ответа"),
                ),
                (
                    "parent_question",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="surveys.answer",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="surveys.question",
                        verbose_name="Вопрос",
                    ),
                ),
                (
                    "survey",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="surveys.survey",
                        verbose_name="Опрос",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ответ",
                "verbose_name_plural": "Ответы",
            },
        ),
    ]
