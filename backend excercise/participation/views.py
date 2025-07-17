from django.shortcuts import render
from rest_framework import viewsets, permissions

from participation.models import Task, UserAnswer, UserQuiz, UserSubjectScore
from participation.serializers import TaskSerializer, UserAnswerSerializer, UserQuizSerializer, UserSubjectScoreSerializer
from users.permissions import IsAdmin, IsTeacher

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

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            # Only show answers for quizzes this student participated in
            return UserAnswer.objects.filter(User_Quiz_ID__User_ID=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        user_quiz = serializer.validated_data.get('User_Quiz_ID')
        if user.role == 'student' and user_quiz.User_ID != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only answer for your own quiz attempts.')
        serializer.save()

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