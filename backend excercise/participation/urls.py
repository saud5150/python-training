from django.urls import path
from participation.answer.views import AnswerAPIView
from participation.score.views import ScoreAPIView
from participation.task.views import TaskAPIView
from participation.quiz.views import QuizAPIView


urlpatterns = [
    # Quiz endpoints
    path('quiz/', QuizAPIView.as_view(), name='quiz-list'),
    path('quiz/<int:pk>/', QuizAPIView.as_view(), name='quiz-detail'),

    # Answer endpoints
    path('answer/', AnswerAPIView.as_view(), name='answer-list'),
    path('answer/<int:pk>/', AnswerAPIView.as_view(), name='answer-detail'),

    # Score endpoints
    path('score/', ScoreAPIView.as_view(), name='score-list'),
    path('score/<int:pk>/', ScoreAPIView.as_view(), name='score-detail'),

    # Task endpoints (UUID primary key)
    path('task/', TaskAPIView.as_view(), name='task-list'),
    path('task/<uuid:pk>/', TaskAPIView.as_view(), name='task-detail'),
]
