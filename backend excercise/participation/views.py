from django.shortcuts import render
from rest_framework import viewsets, permissions

from participation.models import Task, Answer, Quiz, Score
from participation.serializers import TaskSerializer, AnswerSerializer, QuizSerializer, ScoreSerializer
from users.permissions import IsAdmin, IsTeacher

# Create your views here.

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            # Only show answers for quizzes this student participated in
            return Answer.objects.filter(User_Quiz_ID__User_ID=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        user_quiz = serializer.validated_data.get('User_Quiz_ID')
        if user.role == 'student' and user_quiz.User_ID != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only answer for your own quiz attempts.')
        serializer.save()

class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'