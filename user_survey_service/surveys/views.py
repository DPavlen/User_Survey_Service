# from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.db.models import Q
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
    Вычисляем первый вопрос у которого нет родителя и передаем в контекст.
    """
    survey = get_object_or_404(Survey, slug=survey_slug)
    parent_question = survey.questions.filter(parent_question__isnull=True).first()
    if parent_question:
        next_question_url = reverse('surveys:survey_question',
                                    kwargs={'survey_slug': survey.slug,
                                            'question_slug': parent_question.slug})
        print("REVERSE URL", next_question_url)
        context = {
            'survey': survey,
            'parent_question': parent_question,
            'next_question_url': next_question_url,
        }
    else:
        next_question_url = None
        context = {
            'survey': survey,
            'parent_question': None,
            'next_question_url': None,
        }
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
        fields=('id', 'title', 'text', 'slug', 'parent_question'))

    return JsonResponse({'questions': serialized_data}, safe=False)


class SurveyQuestion(View):
    """Форма отправки ответов на опросы."""
    def get_parent_question(self, survey_slug, question_slug=None):
        """Получить родительский вопрос."""
        survey = get_object_or_404(Survey, slug=survey_slug)
        query_params = {'survey': survey, 'parent_question__isnull': True}
        if question_slug:
            query_params['slug'] = question_slug
        parent_question = get_object_or_404(Question, **query_params)
        print("parent_question", parent_question)
        return parent_question

    def get_next_question(self, survey, current_question):
        next_question = None
        if current_question.child_questions.exists():
            next_question = current_question.child_questions.first()
        elif survey.questions.filter(parent_question=current_question).exists():
            next_question = survey.questions.filter(parent_question=current_question).first()
        print("next_question", next_question)
        return next_question

    def get(self, request, survey_slug, question_slug=None):
        survey = get_object_or_404(Survey, slug=survey_slug)
        # Получаем вопрос, у которого parent_question равен None
        parent_question = self.get_parent_question(survey_slug, question_slug)

        if parent_question:
            choices = parent_question.choices.all()
            # Получаем следующий вопрос
            next_question = self.get_next_question(survey, parent_question)

            # Если есть parent_question, возвращаем страницу с подчиненным вопросом
            context = {
                'survey': survey,
                'question': parent_question,
                'user': request.user,
                'choices': choices,  # Передаем варианты ответов
            }
            print("Choices:", context['choices'])
            print("Родитель:", context)
        else:
            # Если нет parent_question, возвращаем страницу с первым вопросом
            first_question = survey.questions.filter(parent_question__isnull=True).first()
            # next_question = self.get_next_question(survey, parent_question)
            choices = first_question.choices.all()
            context = {
                'survey': survey,
                'question': first_question,
                'user': request.user,
                'choices': list(choices),  # Передаем варианты ответов
            }
            print("Ребенок:", first_question)

        print(context)
        return render(request, 'surveys/survey_question.html', context)

    def post(self, request, survey_slug, question_slug):
        try:
            print("Entered the post method")
            survey = get_object_or_404(Survey, slug=survey_slug)
            print("Survey object:", survey)
            question = get_object_or_404(Question, survey=survey, slug=question_slug)
            print("Question object:", question)

            # Проверка наличия атрибута parent_question у предыдущего вопроса
            parent_answer_id = request.POST.get("parent_answer_id")
            parent_answer = get_object_or_404(Answer, id=parent_answer_id) if parent_answer_id else None
            print("Parent Answer object:", parent_answer)

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

            # Определение следующего вопроса
            next_question = None
            if parent_answer and parent_answer.question.child_questions.exists():
                next_question = parent_answer.question.child_questions.first()
                print("Next question from child_questions:", next_question)
            elif survey.questions.filter(parent_question=question).exists():
                next_question = survey.questions.filter(parent_question=question).first()
                print("Next question from filter:", next_question)

            if next_question:
                redirect_url = reverse("surveys:survey_question", args=[survey_slug, next_question.slug])
                print("Redirect URL next_question:", redirect_url)
                return redirect(redirect_url)
            else:
                redirect_url = reverse("surveys:survey_results", args=[survey_slug])
            print("Redirect URL:", redirect_url)
            return redirect(redirect_url)
            # else:
            #     # Перенаправляем на страницу со статистикой
            #     redirect_url = reverse("surveys:survey_results", args=[survey_slug])
            #     return JsonResponse({'redirect': redirect_url})

            # return JsonResponse({'redirect': redirect_url})

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