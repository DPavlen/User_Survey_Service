from django.db import models

from users.models import MyUser


class Survey(models.Model):
    """Модель опросов. 
    У каждого опроса есть вопрос и ответ на него."""
    title = models.CharField(
        "Опрос", 
        unique=True,
        max_length=255,
    )
    description = models.CharField(
        "Полное описание опроса",
        max_length=255,
    )
    slug = models.SlugField(
        "Уникальный слаг опроса",
        unique=True,
        max_length=155,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"


class Question(models.Model):
    """Модель вопросов. Вопрос связан с одним опросом."""
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
    parent_question = models.ForeignKey(
        "self", 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE
    )
   
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Answer(models.Model):
    """Модель ответов. 
    У каждого ответа есть следующие атрибуты:
    соотвествующий автор, опрос и вопрос.
    """
    pub_date = models.DateTimeField(
        "Дата ответа", 
        auto_now_add=True
    )
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="answers",
        verbose_name="Вопрос",
    )
    author = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Автор выбранного ответа",
    )
    choice = models.ForeignKey(
        "surveys.Choice",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="answers",
        verbose_name="Выбранный вариант ответа",
    )

    def __str__(self):
        return self.title 

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"


class Choice(models.Model):
    """Модель выбора варианат ответов к вопросам. 
    """
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name="Выбор",
    )
    text = models.CharField(
        "Текст варианта ответа", 
        max_length=255
    )

    def __str__(self):
        return self.text 

    class Meta:
        verbose_name = "Выбор варианта ответа"
        verbose_name_plural = "Выбор вариантов ответов"