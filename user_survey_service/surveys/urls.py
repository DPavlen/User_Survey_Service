from django.urls import path
from surveys import views

app_name = "surveys"

urlpatterns = [
    path("surveys/", views.survey_list, name="survey_list"),
    path("surveys/<slug:survey_slug>/", views.survey_detail_view, name="survey_detail"),
    path("surveys/<slug:survey_slug>/results/", views.SurveyResultsStatistics.as_view(), name="survey_results"),
    # Ajax загрузка вопросов
    path("surveys/<slug:survey_slug>/load_questions/", views.load_questions, name="load_questions"),
    # path("surveys/<slug:survey_slug>/<slug:question_slug>/", views.SurveyQuestionView.as_view(), name="survey_question"),
    path("surveys/<slug:survey_slug>/submit/", views.SurveySubmitView.as_view(), name="survey_submit"),
]