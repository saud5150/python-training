
from rest_framework import routers

from participation.views import QuizViewSet, AnswerViewSet, ScoreViewSet, TaskViewSet

router = routers.DefaultRouter()

router.register(r'userquizzes', QuizViewSet)
router.register(r'useranswers', AnswerViewSet)
router.register(r'usersubjectscores', ScoreViewSet)
router.register(r'tasks', TaskViewSet)