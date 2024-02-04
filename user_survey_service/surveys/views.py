from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from surveys.models import Survey, Question, Answer
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
    surveys = Survey.objects.all()
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
    }
    return render(request, "surveys/survey_detail_view.html", context)


class Survey_Submit_View(View):
    """Форма отправки ответов на опросы."""
    def get(self, request, pk):
        """Получение ответа."""
        survey = get_object_or_404(Survey, pk=pk)
        questions = survey.questions.all()
        page_obj = get_paginated_objects(questions, request)
        context = {
            'page_obj': page_obj,
        }
        return render(request, "surveys/survey_submit.html", context)

    def post(self, request, pk):
        """Создание ответа."""
        survey = get_object_or_404(Survey, pk=pk)
        questions = survey.question_set.all()
        return redirect("survey_detail", pk=survey.pk)
