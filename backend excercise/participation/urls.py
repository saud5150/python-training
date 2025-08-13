from django.urls import path
from participation.views import QuizAPIView, AnswerAPIView, ScoreAPIView, TaskAPIView

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
