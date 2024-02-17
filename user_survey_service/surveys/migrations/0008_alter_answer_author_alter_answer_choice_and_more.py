# Generated by Django 4.2 on 2024-02-17 11:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("surveys", "0007_remove_answer_unique_question_author"),
    ]

    operations = [
        migrations.AlterField(
            model_name="answer",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="answers_user",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор выбранного ответа",
            ),
        ),
        migrations.AlterField(
            model_name="answer",
            name="choice",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="answers_choice",
                to="surveys.choice",
                verbose_name="Выбранный вариант ответа",
            ),
        ),
        migrations.AlterField(
            model_name="answer",
            name="question",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="answers_question",
                to="surveys.question",
                verbose_name="Вопрос",
            ),
        ),
    ]