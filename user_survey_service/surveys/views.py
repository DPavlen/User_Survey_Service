from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseServerError
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from surveys.models import Survey, Question, Answer, Choice
# from surveys.utils import paginator_context

COUNT_POST = 10

def get_paginated_objects(objects, request):
    """Возвращает объекты с пагинацией."""
    paginator = Paginator(objects, COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

def survey_list(request):
    """Главная страница списка опросов пользователей."""
    # surveys = Survey.objects.all()
    surveys = Survey.objects.raw('SELECT * FROM surveys_survey')
    page_obj = get_paginated_objects(surveys, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, "surveys/index.html", context)

def survey_detail_view(request, pk):
    """Информация о деталях опросов и его вопросов."""
    survey = get_object_or_404(Survey, pk=pk)
    questions = survey.questions.all()
    page_obj = get_paginated_objects(questions, request)
    context = {
        'page_obj': page_obj,
        'survey': survey,
    }
    return render(request, "surveys/survey_detail.html", context)


class SurveySubmitView(View):
    """Форма отправки ответов на опросы."""
    def get(self, request, pk):
        """Получение ответа."""
        survey = get_object_or_404(Survey, pk=pk)
        questions = survey.questions.all()
        # page_obj = get_paginated_objects(questions, request)
        context = {
            'questions': questions,
            'survey': survey,
        }
        return render(request, "surveys/survey_submit.html", context)

    def post(self, request, pk):
        """Создание ответа. 
        Сохранение ответа пользователя(To Do необходимо выбирать из списка ответов!).
        Проверка наличия атрибута parent_question у предыдщего вопроса.
        Перенаправление на страницу со следующим вопросом(по дереву вопросов).
        Перенаправление на страницу со статистикой ответов на вопросы.
        """
        survey = get_object_or_404(Survey, pk=pk)
        questions = survey.questions.all()
        # Получаем ответы usera
        answers = []
        for question in questions:
            question_id = f"question_{question.id}"
            if question.choices.exists():
                # Если вопрос имеет варианты ответов, сохраняем выбранный вариант
                choice_id = request.POST.get(question_id)
                choice = get_object_or_404(Choice, id=choice_id)
                answer = Answer(
                    question=question, 
                    text=choice.text, 
                    survey=survey, 
                    author=request.user,
                    choice=choice
                )
            else:
                # Если вопрос не имеет вариантов ответов, сохраняем введенный текст
                answer_text = request.POST.get(question_id, "")
                answer = Answer(
                    question=question, 
                    text=answer_text, 
                    survey=survey, 
                    author=request.user
                )
            answers.append(answer)

        try:
            Answer.objects.bulk_create(answers)
        except Exception as e:
            return HttpResponseServerError(
                f"Ошибка при сохранении ответа на вопрос: {e}"
                )
        # Определение следующего вопроса, проверка наличия атрибута parent_question 
        next_question = None
        for question in questions:
            if not hasattr(question, "parent_question") or not question.parent_question:
                next_question = question
                break
            else:
                parent_answer = Answer.objects.filter(
                    question=question.parent_question, 
                    survey=survey, 
                    author=request.user).first()
                if parent_answer and parent_answer.text == request.POST.get(
                        f"question_{question.parent_question.id}", ""):
                    next_question = question
                    break

        if next_question:
            return redirect("surveys:survey_detail", pk=survey.pk)
        else:
            pass 
            # Тут будем выводить страницу с результатами статистика

