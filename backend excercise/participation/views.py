from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from participation.models import Task, Answer, Quiz, Score
from participation.serializers import TaskSerializer, AnswerSerializer, QuizSerializer, ScoreSerializer
from users.permissions import IsAdmin, IsAdminOrTeacher, IsTeacher
from drf_spectacular.utils import extend_schema

# Create your views here.
@extend_schema(tags=['Participation'])
class QuizAPIView(APIView):
    serializer_class = QuizSerializer

    def get_permissions(self):
        # Only admin can DELETE
        if self.request.method == 'DELETE':
            return [IsAdmin()]
        # All authenticated users can GET (list/retrieve)
        return [permissions.IsAuthenticated()]
    
    def get(self, request, pk=None):
        if pk:
            quiz = get_object_or_404(Quiz, pk=pk)
            serializer = QuizSerializer(quiz)
            return Response(serializer.data)
        quizzes = Quiz.objects.all()
        serializer = QuizSerializer(quizzes, many = True)
        return Response(serializer.data)
    

    def post(self, request):
        lookup_field = 'id'  

        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        serializer = QuizSerializer(quiz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        serializer = QuizSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        serializer_class = QuizSerializer

        quiz = get_object_or_404(Quiz, pk=pk)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(tags=['Participation', 'Answer'])
class AnswerAPIView(APIView):
    serializer_class = AnswerSerializer
    def get(self, request, pk=None):
        if pk:
            answer = get_object_or_404(Answer, pk=pk)
            serializer = AnswerSerializer(answer)
            return Response(serializer.data)
        answers = Answer.objects.all()
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AnswerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        serializer = AnswerSerializer(answer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        serializer = AnswerSerializer(answer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        answer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Participation', 'Score'])
class ScoreAPIView(APIView):
    permission_classes = [IsAdminOrTeacher]
    serializer_class = ScoreSerializer
    def get(self, request, pk=None):
        if pk:
            score = get_object_or_404(Score, pk=pk)
            serializer = ScoreSerializer(score)
            return Response(serializer.data)
        scores = Score.objects.all()
        serializer = ScoreSerializer(scores, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ScoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        score = get_object_or_404(Score, pk=pk)
        serializer = ScoreSerializer(score, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        score = get_object_or_404(Score, pk=pk)
        serializer = ScoreSerializer(score, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        score = get_object_or_404(Score, pk=pk)
        score.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(tags=['Participation', 'Task'])
class TaskAPIView(APIView):

    serializer_class = TaskSerializer
    def get(self, request, pk=None):
        if pk:
            task = get_object_or_404(Task, pk=pk)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
