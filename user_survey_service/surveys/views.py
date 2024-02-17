# from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.db.models import Q
from django.http import HttpResponseServerError, JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, \
    HttpResponseBadRequest
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
    Вычисляем первый вопрос у которого нет родителя и передаем в контекст.
    """
    # survey = get_object_or_404(Survey, slug=survey_slug)
    try:
        survey = Survey.objects.get(slug=survey_slug)
    except Survey.DoesNotExist:
        # Обработка случая, когда опрос не найден
        return HttpResponseNotFound("Опрос не найден")

    # survey = Survey.objects.filter(), slug=survey_slug)
    parent_question = survey.questions.filter(degree_question=Question.DegreeQuestion.PARENT).first()
    print("PARENT_QUESTION:", parent_question)
    if parent_question:
        parent_question_url = reverse('surveys:survey_question',
                                      kwargs={'survey_slug': survey.slug,
                                              'question_slug': parent_question.slug})
        print("REVERSE URL", parent_question_url)
        context = {
            'survey': survey,
            'parent_question': parent_question,
            'parent_question_url': parent_question_url,
        }
        # else:
        #     next_question_url = None
        #     context = {
        #         'survey': survey,
        #         'parent_question': None,
        #         'next_question_url': None,
        #     }
        print("DETAIL:", context)
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
        fields=('id', 'title', 'text', 'slug', 'degree_question'))

    return JsonResponse({'questions': serialized_data}, safe=False)


class SurveyQuestion(View):
    """Форма отправки ответов на опросы."""

    def get_parent_question(self, survey_slug, question_slug=None):
        """Получить родительский вопрос."""
        # survey = get_object_or_404(Survey, slug=survey_slug)
        survey = Survey.objects.get(slug=survey_slug)
        query_params = {'survey': survey,
                        'degree_question': Question.DegreeQuestion.PARENT
                        }
        if question_slug:
            query_params['slug'] = question_slug
        parent_question = get_object_or_404(Question, **query_params)
        print("parent_question", parent_question)
        return parent_question

    def get_next_question(self, survey, current_question, user=None):
        # user_answer = Answer.objects.filter(question=current_question, author=user).first()
        user_answer = user.answers_user.filter(question=current_question).first()
        if user_answer and user_answer.choice and user_answer.choice.child_question:
            # Если у пользователя есть ответ с выбранным вариантом, возвращаем следующий вопрос
            return user_answer.choice.child_question
        elif current_question.choices_child.exists():
            # Если у текущего вопроса есть дочерние вопросы в таблице Choice,
            # возвращаем первый дочерний вопрос
            return current_question.choices_child.first()
        return None

    def get(self, request, survey_slug, question_slug=None):
        survey = get_object_or_404(Survey, slug=survey_slug)
        parent_question = self.get_parent_question(survey_slug, question_slug)
        print("МЕТОД get. degree_question", parent_question)
        # Извлекаем choice_id из запроса
        choice_id = request.GET.get('choice_id')
        print("МЕТОД get.choice_id", choice_id)
        if parent_question:
            choices = parent_question.choices.all()
            # Получаем следующий вопрос
            choices_list = list(choices)
            next_question = self.get_next_question(survey, parent_question, user=request.user)

            if next_question:
                next_question_slug = next_question.slug
                # Создаем URL для следующего вопроса
                next_question_url = reverse('surveys:survey_question',
                                            kwargs={'survey_slug': survey_slug,
                                                    'question_slug': next_question_slug})
                if next_question_url:
                    print("GET.next_question_url:", next_question_url)
            else:
                next_question_slug = None
                next_question_url = None

            context = {
                # 'survey': parent_question.survey,
                'survey': survey,
                'question': parent_question,
                'user': request.user,
                'choices': choices_list,
                'next_question': next_question,  # Добавляем next_question в контекст
                'next_question_slug': next_question_slug,  # Добавляем next_question_slug в контекст
                'choice_id': choice_id,
                'next_question_url': next_question_url,
            }
            print("GET.Choices:", context['choices'])
            print("GET.Родитель:", context)
            print("GET.next_question:", next_question)
            print("GET.next_question_slug:", next_question_slug)
            print("GET.next_question_url:", next_question_url)
            return render(request, 'surveys/survey_question.html', context)

    def post(self, request, survey_slug, question_slug):
        try:
            print("POST.survey_slug:", survey_slug)
            print("POST.question_slug:", question_slug)
            # survey = get_object_or_404(Survey, slug=survey_slug)
            survey = Survey.objects.get(slug=survey_slug)
            # question = get_object_or_404(Question, survey=survey, slug=question_slug)
            question = Question.objects.get(survey=survey, slug=question_slug)
            # Извлекаем choice_id из POST-запроса
            choice_id = request.POST.get(f"question_{question.id}")
            print("POST.Question object:", question)

            # Получаем ответы пользователя
            answers = []
            question_id = f"question_{question.id}"
            print("POST.Question ID:", question_id)

            if question.choices.exists():
                # Если вопрос имеет варианты ответов, сохраняем выбранный вариант
                print("POST.Choice ID:", choice_id)
                if choice_id:
                    # choice = get_object_or_404(Choice, id=choice_id)
                    choice = Choice.objects.get(id=choice_id)
                    answer = Answer(
                        question=question,
                        author=request.user,
                        choice=choice,
                    )
                    answers.append(answer)
            try:
                Answer.objects.bulk_create(answers)
            except Exception as e:
                print(f"Error during bulk_create: {e}")
                return HttpResponseServerError(
                    f"Ошибка при сохранении ответа на вопрос: {e}"
                )

            # Получаем ответ пользователя для текущего вопроса
            # user_answer = Answer.objects.filter(question=question, author=request.user).first()
            user_answer = request.user.answers_user.filter(question=question).first()

            if not user_answer:
                # Если пользователя нет в ответах, вернуть какое-то сообщение
                return HttpResponseBadRequest("Не ответа у пользователя.")

            if question.choices.exists() and user_answer:
                # Если вопрос имеет варианты ответов и у пользователя уже есть ответ
                if user_answer.choice and user_answer.choice.child_question:
                    # Если у пользователя есть выбранный choice и связанный child_question
                    next_question = user_answer.choice.child_question
                    print("POST.выбранный choice и связанный child_question:", next_question)
                elif question.choices_child.exists():
                    # Если у текущего вопроса есть дочерние вопросы в таблице Choice,
                    # ищем следующий вопрос среди дочерних вопросов
                    next_question = question.choices_child.first()
                else:
                    # Если дочерних вопросов нет, переходим к следующему вопросу в опросе
                    next_question = survey.questions.filter(parent_question=question).first()

                if next_question:
                    print("POST.type()", type(next_question))
                    print("POST.next_question", next_question)
                    print("POST.next_question.slug", next_question.slug)

                    return HttpResponseRedirect(reverse("surveys:survey_question", kwargs={
                        'survey_slug': survey_slug,
                        'question_slug': next_question.slug,

                    }))
                    # return HttpResponseRedirect(
                    #     reverse("surveys:survey_question", args=[survey_slug, next_question.slug], current_app=survey._meta.surveys))

                return HttpResponseBadRequest("Next question not found.")
                # if next_question:
                #     print("next_question.slug", next_question.slug)
                #     return redirect(reverse("surveys:survey_question",
                #                             args=[survey_slug, next_question.slug]))
                # else:
                #     redirect_url = reverse("surveys:survey_results", args=[survey_slug])
                #     print("СТАТИСТИКА ОТВЕТОВ:", redirect_url)
                #     return redirect(redirect_url)

            # Добавьте обработку случая, когда ответа нет или вопрос не имеет вариантов ответов
            return HttpResponse("Invalid request or question setup.")

        except Exception as e:
            print(f"Ошибка в методе post: {e}")
            return HttpResponseServerError(
                f"Ошибка в методе post: {e}"
            )


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
