# from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.db.models import Q
from django.http import HttpResponseServerError, JsonResponse, HttpResponse
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
    survey = get_object_or_404(Survey, slug=survey_slug)
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
        survey = get_object_or_404(Survey, slug=survey_slug)
        query_params = {'survey': survey,
                        'degree_question': Question.DegreeQuestion.PARENT
                        }
        if question_slug:
            query_params['slug'] = question_slug
        parent_question = get_object_or_404(Question, **query_params)
        print("parent_question", parent_question)
        return parent_question

    def get_next_question(self, survey, current_question, user=None):
        next_question = None
        user_answer = Answer.objects.filter(question=current_question, author=user).first()
        if user_answer and user_answer.choice:
            # Если у пользователя есть ответ с выбранным вариантом, ищем следующий вопрос
            next_question = user_answer.choice.child_question
        elif current_question.choices_child.exists():
            # Если у текущего вопроса есть дочерние вопросы в таблице Choice,
            # ищем следующий вопрос среди дочерних вопросов
            next_question = current_question.choices_child.first()
        return next_question

    def get(self, request, survey_slug, question_slug=None):
        survey = get_object_or_404(Survey, slug=survey_slug)
        # Получаем вопрос, у которого degree_question=Question.DegreeQuestion.PARENT
        degree_question = self.get_parent_question(survey_slug, question_slug)

        if degree_question:
            choices = degree_question.choices.all()
            # Получаем следующий вопрос
            choices_list = list(choices)
            next_question = self.get_next_question(survey, degree_question)
            # Если есть degree_question, возвращаем страницу с подчиненным вопросом
            context = {
                'survey': survey,
                'question': degree_question,
                'user': request.user,
                'choices': choices_list,
                'next_question': next_question,  # Добавляем next_question в контекст
            }
            print("Choices:", context['choices'])
            print("Родитель:", context)

        else:
            # Получаем первый вопрос с child_question=True и связываем с ответом author
            child_question = survey.questions.filter(choices__child_question__isnull=False).first()
            user_answer = Answer.objects.filter(question=child_question, author=request.user).first()

            if user_answer and user_answer.choice and user_answer.choice.child_question:
                # Если у пользователя есть ответ с выбранным вариантом и связанным дочерним вопросом
                next_question = user_answer.choice.child_question
            else:
                # Иначе используем первый вариант ответа, связанный с дочерним вопросом
                next_question = child_question.choices.filter(child_question__isnull=False).first().child_question

            choices = child_question.choices.all()
            choices_list = list(choices)
            context = {
                'survey': survey,
                'question': child_question,
                'user': request.user,
                'choices': choices_list,
                'next_question': next_question,
            }
            print("Ребенок:", child_question)

            print(context)
        return render(request, 'surveys/survey_question.html', context)

    def post(self, request, survey_slug, question_slug):
        try:
            # survey = get_object_or_404(Survey, slug=survey_slug)
            survey = Survey.objects.get(slug=survey_slug)
            question = get_object_or_404(Question, survey=survey, slug=question_slug)
            print("Question object:", question)

            # Получаем ответы пользователя
            answers = []
            question_id = f"question_{question.id}"
            print("Question ID:", question_id)

            if question.choices.exists():
                # Если вопрос имеет варианты ответов, сохраняем выбранный вариант
                choice_id = request.POST.get(question_id)
                print("Choice ID:", choice_id)
                if choice_id:
                    choice = get_object_or_404(Choice, id=choice_id)
                    answer = Answer(
                        question=question,
                        author=request.user,
                        choice=choice,
                    )
                    answers.append(answer)
            else:
                # Если вопрос не имеет вариантов ответов, добавляем соответствующий текст
                answer_text = request.POST.get(question_id, "")
                print("Answer Text:", answer_text)
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
                print(f"Error during bulk_create: {e}")
                return HttpResponseServerError(
                    f"Ошибка при сохранении ответа на вопрос: {e}"
                )

            # Получаем ответ пользователя для текущего вопроса
            user_answer = Answer.objects.filter(question=question, author=request.user).first()

            if question.choices.exists() and user_answer:
                # Если вопрос имеет варианты ответов и у пользователя уже есть ответ
                if user_answer.choice and user_answer.choice.child_question:
                    # Если у пользователя есть выбранный choice и связанный child_question
                    next_question = user_answer.choice.child_question
                    print("выбранный choice и связанный child_question:", next_question)
                elif question.choices_child.exists():
                    # Если у текущего вопроса есть дочерние вопросы в таблице Choice,
                    # ищем следующий вопрос среди дочерних вопросов
                    next_question = question.choices_child.first()
                else:
                    # Если дочерних вопросов нет, переходим к следующему вопросу в опросе
                    next_question = survey.questions.filter(parent_question=question).first()

                if next_question:
                    print("next_question.slug", next_question.slug)
                    return redirect(reverse("surveys:survey_question",
                                            args=[survey_slug, next_question.slug]))
                # else:
                #     redirect_url = reverse("surveys:survey_results", args=[survey_slug])
                #     print("СТАТИСТИКА ОТВЕТОВ:", redirect_url)
                #     return redirect(redirect_url)

            # Добавьте обработку случая, когда ответа нет или вопрос не имеет вариантов ответов
            return HttpResponse("Invalid request or question setup.")

        except Exception as e:
            print(f"Error in post method: {e}")
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