from django.db import models


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
        "Уникальный слаг",
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
    text = models.TextField()
    survey = models.ForeignKey(
        Survey, 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="question",
        verbose_name="Опрос",
    )
   
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Answer(models.Model):
    """Модель ответов. Ответ связан с одним вопросом."""
    title = models.CharField(
        "Ответ", 
        unique=True,
        max_length=255
    )
    text = models.TextField()
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="answer",
        verbose_name="Вопрос",
    )
   
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"