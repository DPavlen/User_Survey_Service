# Generated by Django 4.2 on 2024-02-04 14:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("surveys", "0002_answer_author_answer_survey_alter_answer_question"),
    ]

    operations = [
        migrations.AlterField(
            model_name="survey",
            name="slug",
            field=models.SlugField(
                max_length=155, unique=True, verbose_name="Уникальный слаг опроса"
            ),
        ),
    ]