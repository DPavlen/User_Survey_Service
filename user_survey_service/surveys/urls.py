from django.urls import path
from . import views

app_name = "surveys"

urlpatterns = [
    path("surveys/", views.survey_list, name="survey_list"),
    path("surveys/<int:pk>/", views.survey_detail_view, name="survey_detail_view"),
    path("surveys/<int:pk>/submit/", views.Survey_Submit_View.as_view(), name="survey_submit"),

]