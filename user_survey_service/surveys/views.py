from django.contrib.auth.decorators import login_required
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from surveys.models import Survey, Question, Answer

COUNT_POST = 10

def index(request):
    """Главная страница списка опросов пользователей."""
    surveys = Survey.objects.all()
    context = {
        'Опросы': surveys
        }
    print(surveys)
    return render(request, "surveys/index.html", context )
