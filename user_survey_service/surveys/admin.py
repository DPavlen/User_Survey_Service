from django.contrib import admin

from surveys.models import Survey, Question, Answer


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "description", "slug")
    list_display_links = ("title",)
    search_fields = ("title",)
    empty_value_display = "-пусто-"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "text")
    list_display_links = ("title",)
    search_fields = ("title",)
    empty_value_display = "-пусто-"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("pk","author", "title", "text")
    list_display_links = ("title", "author")
    search_fields = ("title",)
    empty_value_display = "-пусто-"