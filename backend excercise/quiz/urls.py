from rest_framework import routers

from participation.views import TaskViewSet, UserAnswerViewSet, UserQuizViewSet, UserSubjectScoreViewSet
from quizzes.views import QuestionViewSet, QuizViewSet, SubjectViewSet
from users.views import UserViewSet
from .views import *
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'userquizzes', UserQuizViewSet)
router.register(r'useranswers', UserAnswerViewSet)
router.register(r'usersubjectscores', UserSubjectScoreViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('questions/upload_csv/', QuestionCSVUploadView.as_view(), name='question-upload-csv'),
    path('', include(router.urls)),
] 