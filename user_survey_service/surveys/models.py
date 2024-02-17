from django.db import models
from django.utils.text import slugify
from django.db.models import UniqueConstraint
from django.urls import reverse
from autoslug import AutoSlugField
from transliterate import translit

from users.models import MyUser


def get_slug(instance):
    """Транслитерованный слаг для модели опросов и вопросов."""
    return translit(
        instance.title,
        'ru',
        reversed=True)


class Survey(models.Model):
    """Модель опросов. 
    В каждом опросе вопросы и ответы на него."""
    # DoesNotExist = None
    # objects = None
    DoesNotExist = None
    objects = None
    title = models.CharField(
        "Опрос",
        unique=True,
        max_length=255,
    )
    slug = AutoSlugField(
        "Слаг опроса",
        populate_from=get_slug,
        unique=True,
        max_length=155,
    )
    description = models.TextField(
        "Тематика опроса",
    )


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"


class Question(models.Model):
    """Модель вопросов. Вопрос связан с одним опросом."""
    objects = None

    class DegreeQuestion(models.TextChoices):
        """
        Определение степени вопроса.
        """
        PARENT = "parent"
        CHILD = "child"
        LAST_CHILD = "last_child"

    title = models.CharField(
        "Вопрос",
        unique=True,
        max_length=255
    )
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="questions",
        verbose_name="Опрос",
    )
    degree_question = models.CharField(
        # "self",
        null=True,
        blank=True,
        # related_name="child_questions",
        choices=DegreeQuestion.choices,
        default=DegreeQuestion.CHILD,
        max_length=10,
    )
    slug = AutoSlugField(
        "Слаг вопроса",
        populate_from=get_slug,
        unique=True,
        max_length=155,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Choice(models.Model):
    """Модель выбора варианта ответов к вопросам.
    """
    objects = None
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name="Текущий вопрос",
    )
    text = models.CharField(
        "Текст варианта ответа",
        max_length=255
    )
    child_question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="choices_child",
        verbose_name="Следующий вопрос",
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Выбор варианта ответа"
        verbose_name_plural = "Выбор вариантов ответов"


class Answer(models.Model):
    """Модель ответов. 
    У каждого ответа есть следующие атрибуты:
    соотвествующий автор, опрос и вопрос.
    """
    objects = None
    pub_date = models.DateTimeField(
        "Дата ответа",
        auto_now_add=True
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="answers_question",
        verbose_name="Вопрос",
    )
    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name="answers_user",
        # related_query_name="answers_user",
        verbose_name="Автор выбранного ответа",
    )
    choice = models.ForeignKey(
        "surveys.Choice",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="answers_choice",
        verbose_name="Выбранный вариант ответа",
    )

    def __str__(self):
        # return self.question
        return f"{self.author} - {self.question}"

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        # constraints = [
        #     UniqueConstraint(
        #         fields=("question", "author"),
        #         name="unique_question_author",
        #     )
        # ]

# class Choice(models.Model):
#     """Модель выбора варианта ответов к вопросам.
#     """
#     objects = None
#     question = models.ForeignKey(
#         Question,
#         on_delete=models.CASCADE,
#         related_name="choices",
#         verbose_name="Текущий вопрос",
#     )
#     text = models.CharField(
#         "Текст варианта ответа",
#         max_length=255
#     )
#     child_question = models.ForeignKey(
#         Question,
#         on_delete=models.CASCADE,
#         null=True,
#         blank=True,
#         related_name="choices_child",
#         verbose_name="Следующий вопрос",
#     )
#
#     def __str__(self):
#         return self.text
#
#     class Meta:
#         verbose_name = "Выбор варианта ответа"
#         verbose_name_plural = "Выбор вариантов ответов"
