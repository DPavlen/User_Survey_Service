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

def survey_detail_view(request, survey_slug):
    """Информация о деталях опросов и его вопросов."""
    survey = get_object_or_404(Survey, slug=survey_slug)
    # questions = survey.questions.raw()
    questions = survey.questions.all()
    # page_obj = get_paginated_objects(questions, request)
    context = {
        'questions': questions,
        # 'page_obj': page_obj,
        'survey': survey,
    }
    return render(request, "surveys/survey_detail.html", context)


class SurveySubmitView(View):
    """Форма отправки ответов на опросы."""
    def get(self, request, survey_slug, current_question_id=None):
        """Получение ответа."""
        survey = get_object_or_404(Survey, slug= survey_slug)
        questions = survey.questions.filter(parent_question__isnull=True)
        answered_questions = Answer.objects.filter(
            survey=survey, author=request.user).values_list('question_id', flat=True)
        # Фильтрация вопросов: только те, у которых нет родительского вопроса и на которые пользователь еще не ответил
        questions = questions.exclude(id__in=answered_questions)

        context = {
            'questions': questions,
            'survey': survey,
        }
        return render(request, "surveys/survey_submit.html", context)

    def post(self, request, survey_slug):
        """Создание ответа. 
        Сохранение ответа пользователя(необходимо выбирать из списка ответов!).
        Проверка наличия атрибута parent_question у предыдущего вопроса.
        Перенаправление на страницу со следующим вопросом(по дереву вопросов).
        Перенаправление на страницу со статистикой ответов на вопросы.
        """
        survey = get_object_or_404(Survey, slug=survey_slug)
        questions = survey.questions.all()
        
        # Фильтрация вопросов: только те, у которых нет родительского вопроса
        questions = [question for question in questions if not question.parent_question]

        # Получаем ответы пользователя
        answers = []
        for question in questions:
            question_id = f"question_{question.id}"
            if question.choices.exists():
                # Если вопрос имеет варианты ответов, сохраняем выбранный вариант
                choice_id = request.POST.get(question_id)
                if choice_id:
                    choice = get_object_or_404(Choice, id=choice_id)
                    answer = Answer(
                        question=question, 
                        author=request.user,
                        choice=choice
                    )
                    answers.append(answer)
            else:
                # Если вопрос не имеет вариантов ответов, добавляем соответствующий текст
                answer_text = request.POST.get(question_id, "")
                if answer_text:
                    answer = Answer(
                        question=question, 
                        author=request.user,
                        text=answer_text
                    )
                    answers.append(answer)

        try:
            Answer.objects.bulk_create(answers)
        except Exception as e:
            return HttpResponseServerError(
                f"Ошибка при сохранении ответа на вопрос: {e}"
            )

        # Определение следующего вопроса
        next_question = None
        for question in questions:
            if not question.parent_question_id:
                next_question = question
                break
            else:
                parent_answer = Answer.objects.filter(
                    question=question.parent_question,
                    survey=survey,
                    author=request.user
                ).first()
                if parent_answer and parent_answer.text == request.POST.get(
                        f"question_{question.parent_question.id}", ""):
                    next_question = question
                    break

        if next_question:
            return redirect("surveys:survey_detail", slug=survey_slug)
        else:
            return redirect("surveys:survey_results", slug=survey_slug)


class SurveyResultsStatistics(View):
    """Отображение результатов статистики."""
    def get(self, request, pk):
        survey = get_object_or_404(Survey, pk=pk)
        questions = survey.questions.all()
        results = []

        total_participants = Answer.objects.filter(question__survey=survey).count()

        for question in questions:
            answers = Answer.objects.filter(question=question, question__survey=survey)
            answer_count = answers.count()
            answer_percentage = 0
            if total_participants > 0:
                answer_percentage = (answer_count / total_participants) * 100

            option_stats = []
            for choice in question.choices.all():
                option_count = answers.filter(choice=choice).count()
                option_percentage = 0
                if total_participants > 0:
                    option_percentage = (option_count / total_participants) * 100
                option_stats.append((choice.text, option_count, option_percentage))

            results.append((question.title, answer_count, answer_percentage, option_stats))

        # return render(request, 'surveys:survey_results.html', {'survey': survey, 'results': results})
        return render(request, 'surveys/survey_results.html', {'survey': survey, 'results': results})