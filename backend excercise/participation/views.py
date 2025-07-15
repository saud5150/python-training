from django.shortcuts import render
from rest_framework import viewsets, permissions

from participation.models import Task, UserAnswer, UserQuiz, UserSubjectScore
from participation.serializers import TaskSerializer, UserAnswerSerializer, UserQuizSerializer, UserSubjectScoreSerializer

# Create your views here.

class UserQuizViewSet(viewsets.ModelViewSet):
    queryset = UserQuiz.objects.all()
    serializer_class = UserQuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'User_Quiz_Id'

class UserAnswerViewSet(viewsets.ModelViewSet):
    queryset = UserAnswer.objects.all()
    serializer_class = UserAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'User_Answer_Id'

class UserSubjectScoreViewSet(viewsets.ModelViewSet):
    queryset = UserSubjectScore.objects.all()
    serializer_class = UserSubjectScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'User_Subject_Score_ID'

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'Task_ID'