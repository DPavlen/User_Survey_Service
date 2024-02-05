from django.urls import path
from surveys import views

app_name = "surveys"

urlpatterns = [
    path("surveys/", views.survey_list, name="survey_list"),
    path("surveys/<int:pk>/", views.survey_detail_view, name="survey_detail"),
    path("surveys/<int:pk>/submit/", views.SurveySubmitView.as_view(), name="survey_submit"),
]