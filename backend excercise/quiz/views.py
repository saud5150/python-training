from rest_framework import viewsets, permissions
from .models import *
from .serializers import *

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'User_ID'
    ordering_fields = ['User_ID', 'email', 'name']
    ordering = ['User_ID']
    filterset_fields = ['User_ID', 'email', 'name']
    search_fields = ['email', 'name']

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'Subject_ID'

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'Quiz_ID'

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'Question_ID'

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
