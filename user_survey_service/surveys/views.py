# from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.http import HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from .models import Survey, Question, Choice, Answer

# import models
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
    """
    Информация о деталях опросов и его вопросов.
    """
    survey = get_object_or_404(Survey, slug=survey_slug)
    parent_question = survey.questions.filter(parent_question__isnull=False).first()
    if parent_question:
        next_question_url = reverse('surveys:survey_question',
                                    kwargs={'survey_slug': survey.slug,
                                            'question_slug': parent_question.slug})
    else:
        next_question_url = None
    context = {
        'survey': survey,
        'parent_question': parent_question.slug if parent_question else None,
        'next_question_url': next_question_url,
    }
    print(context)
    return render(request, "surveys/survey_detail.html", context)


def load_questions(request, survey_slug):
    """
    Представление обрабатываемое AJAX-запросами и возврат данных в формате JSON.
    """
    survey = get_object_or_404(Survey, slug=survey_slug)
    questions = survey.questions.all()
    
    # Используем json.dumps для корректной сериализации
    serialized_data = serialize(
        'json',
        questions,
        fields=('id', 'title', 'text', 'slug', 'parent_question'))

    return JsonResponse({'questions': serialized_data}, safe=False)


class SurveyQuestion(View):
    """Форма отправки ответов на опросы."""
    def get(self, request, survey_slug, question_slug):
        print('QQQQQQQ')
        survey = get_object_or_404(Survey, slug=survey_slug)
        print(survey)
        # Получаем вопрос, у которого parent_question равен None
        question = get_object_or_404(
            Question,
            survey=survey,
            parent_question__isnull=True
        )
        print('QQQQQQQ')
        # # Используем метод get_survey_question_url для получения URL
        # survey_question_url = question.get_survey_question_url()
        #
        # # Получаем следующий вопрос
        # next_question = question.get_next_question()
        #
        # # Если есть следующий вопрос, формируем URL и переходим на него
        # if next_question:
        #     next_question_url = next_question.get_survey_question_url()
        #     return redirect(next_question_url)

        context = {
            'survey': survey,
            'question': question,
            # 'survey_question_url': survey_question_url,
            # 'next_question': next_question,
        }
        print(context)
        # Добавим проверку на наличие следующего вопроса перед передачей в контекст
        # if next_question:
        #     context['next_question_url'] = next_question.get_survey_question_url()

        return render(request, 'surveys/survey_question.html', context)



class SurveySubmitView(View):
    """Форма отправки ответов на опросы."""
    def get(self, request, survey_slug, question_slug):
        """Получение текущего опроса и переход к вопросу."""
        survey = get_object_or_404(Survey, slug=survey_slug)
        question = get_object_or_404(Question, survey=survey, slug=question_slug)

        next_question = self.get_next_question(survey, question.order)

        context = {
            'survey': survey,
            'question': question,
            'next_question': next_question,
            'next_question_url': self.get_survey_question_url(survey_slug, next_question.slug) if next_question else None,
        }
        return render(request, 'surveys/survey_question.html', context)

    def get_survey_question_url(self, survey_slug, question_slug):
        """Получение URL для следующего вопроса."""
        return reverse("surveys:survey_submit", kwargs={'survey_slug': survey_slug, 'question_slug': question_slug})


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
            return redirect("surveys:survey_detail", survey_slug=survey_slug)
        else:
            return redirect("surveys:survey_results", survey_slug=survey_slug)


class SurveyResultsStatistics(View):
    """Отображение результатов статистики."""
    def get(self, request, survey_slug):
        survey = get_object_or_404(Survey, slug=survey_slug)
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

        return render(
            request,
            'surveys/survey_results.html',
            {'survey': survey, 'results': results}
        )