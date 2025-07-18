from rest_framework import routers
from quiz.views import QuestionViewSet, QuizViewSet, SubjectViewSet
from .views import *
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'quiz', QuizViewSet)
router.register(r'questions', QuestionViewSet)


urlpatterns = [
    path('quiz/assign_teacher/', AssignTeacherToQuizView.as_view(), name='assign-teacher-to-quiz'),
    
    path('questions/upload_csv/', QuestionCSVUploadView.as_view(), name='question-upload-csv'),
    path('', include(router.urls)),
] 