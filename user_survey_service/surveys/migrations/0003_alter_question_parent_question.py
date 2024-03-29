# Generated by Django 4.2 on 2024-02-13 15:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("surveys", "0002_alter_question_parent_question"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="parent_question",
            field=models.TextField(
                blank=True,
                choices=[
                    ("parent", "Parent"),
                    ("child", "Child"),
                    ("last_child", "Other"),
                ],
                default="child",
                max_length=255,
                null=True,
            ),
        ),
    ]
