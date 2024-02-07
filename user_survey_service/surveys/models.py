from django.db import models
from django.db.models import UniqueConstraint
from django.urls import reverse
from autoslug import AutoSlugField
from transliterate import translit

from users.models import MyUser


def get_slug(instance):
    """Транслитерованный слаг для модели опросов."""
    return translit(
        instance.title, 
        'ru', 
        reversed=True)


class Survey(models.Model):
    """Модель опросов. 
    В каждом опросе: вопросы и ответы на него."""
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
    def get_absolute_url(self):
        """
        Получение ссылки для html survey_detail со слагом опроса.
        """
        return reverse(
            "surveys:survey_detail", 
            kwargs={'slug': self.slug}
        )
    
    def get_submit_url(self):
        """
        Получение ссылки для html survey_submit со слагом опроса.
        """
        return reverse(
            "surveys:survey_submit", 
            kwargs={'slug': self.slug}
        )
    
    def get_submit_url(self):
        """
        Получение ссылки для html survey_results со слагом опроса.
        """
        return reverse(
            "surveys:survey_results", 
            kwargs={'slug': self.slug}
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
    slug = AutoSlugField(
        "Слаг вопроса",
        populate_from=get_slug,
        unique=True,
        max_length=155,
    )
    def get_next_question(self):
        """
        Возврат объекта следующего вопроса-родителя.
        """
        try:
            next_question = Question.objects.get(
                parent_question=None, order__gt=self.order, survey=self.survey
            )
            return next_question
        except Question.DoesNotExist:
            return None

   
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
        return str(self.question)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        constraints = [
            UniqueConstraint(
                fields=("question", "author"),
                name="unique_question_author",
            )
        ]

class Choice(models.Model):
    """Модель выбора варианта ответов к вопросам. 
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