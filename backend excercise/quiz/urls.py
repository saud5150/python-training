from rest_framework import routers
from .views import *
from django.urls import path, include



urlpatterns = [    # Token endpoints
    path('subjects/', SubjectListCreateView.as_view(), name='subject-list-create'),
    path('subjects/<int:id>/', SubjectDetailView.as_view(), name='subject-detail'),
    path('quizzes/', QuizListCreateView.as_view(), name='quiz-list-create'),
    path('quizzes/<int:id>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/assign_teacher/', AssignTeacherToQuizView.as_view(), name='assign-teacher-to-quiz'),
    path('questions/', QuestionListCreateView.as_view(), name='question-list-create'),
    path('questions/<int:id>/', QuestionDetailView.as_view(), name='question-detail'),
    path('questions/upload_csv/', QuestionCSVUploadView.as_view(), name='question-upload-csv'),

] 