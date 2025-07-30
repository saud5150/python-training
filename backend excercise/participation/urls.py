
from django.urls import include, path
from rest_framework import routers

from participation.views import QuizAPIView, AnswerAPIView, ScoreAPIView, TaskAPIView


urlpatterns = [
    path('quiz/', QuizAPIView.as_view()),
    path('answer/', AnswerAPIView.as_view()),
    path('score/', ScoreAPIView.as_view()),
    path('task/', TaskAPIView.as_view()),
]