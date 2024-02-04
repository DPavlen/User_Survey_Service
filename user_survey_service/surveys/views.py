from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
# from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from surveys.models import Survey, Question, Answer
# from surveys.utils import paginator_context

COUNT_POST = 10


def index(request):
    """Главная страница списка опросов пользователей."""
    surveys = Survey.objects.all()
    paginator = Paginator(surveys, COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    print(surveys)
    return render(request, "surveys/index.html", context )
