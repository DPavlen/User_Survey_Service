from django.contrib import admin

from surveys.models import Survey, Question, Answer, Choice


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    list_display_links = ("pk", "title",)
    search_fields = ("pk", "title",)
    empty_value_display = "-пусто-"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "survey", "parent_question", "slug")
    list_display_links = ("title",)
    search_fields = ("title",)
    empty_value_display = "-пусто-"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("pk", "question", "author", "choice", "pub_date")
    list_display_links = ("question",)
    search_fields = ("title",)
    empty_value_display = "-пусто-"


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("pk", "question", "text")
    list_display_links = ("question",)
    search_fields = ("question",)
    empty_value_display = "-пусто-"