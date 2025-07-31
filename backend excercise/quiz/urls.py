from rest_framework import routers
from .views import *
from django.urls import path, include



urlpatterns = [    # Token endpoints
    path('subjects/', SubjectView.as_view(), name='subject-list-create'),
    path('subjects/<int:id>/', SubjectView.as_view(), name='subject-detail'),
    path('quizzes/', QuizView.as_view(), name='quiz-list-create'),
    path('quizzes/<int:id>/', QuizView.as_view(), name='quiz-detail'),
    path('quizzes/assign_teacher/', AssignTeacherToQuizView.as_view(), name='assign-teacher-to-quiz'),
    path('questions/', QuestionView.as_view(), name='question-list-create'),
    path('questions/<int:id>/', QuestionView.as_view(), name='question-detail'),
    path('questions/upload_csv/', QuestionCSVUploadView.as_view(), name='question-upload-csv'),

] 