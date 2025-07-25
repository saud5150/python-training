
from django.urls import include, path
from rest_framework import routers

from participation.views import QuizViewSet, AnswerViewSet, ScoreViewSet, TaskViewSet

router = routers.DefaultRouter()

router.register(r'quiz', QuizViewSet)
router.register(r'answer', AnswerViewSet)
router.register(r'score', ScoreViewSet)
router.register(r'task', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]