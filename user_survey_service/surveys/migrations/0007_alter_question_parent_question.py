# Generated by Django 4.2 on 2024-02-11 22:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("surveys", "0006_alter_question_parent_question"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="parent_question",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="surveys.question",
            ),
        ),
    ]
