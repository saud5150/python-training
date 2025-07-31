from venv import logger
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from jsonschema import ValidationError
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from participation.models import Task, Answer, Quiz, Score
from participation.permissions import AnswerPermission, IsAdminOrReadOnly
from participation.serializers import TaskSerializer, AnswerSerializer, QuizSerializer, ScoreSerializer
from participation.base_views import ParticipationBaseView
from users.permissions import IsAdmin, IsAdminOrTeacher, IsTeacher
from drf_spectacular.utils import extend_schema

# Create your views here.
@extend_schema(tags=['Participation'])
class QuizAPIView(ParticipationBaseView):
    serializer_class = QuizSerializer
    permission_classes = [IsAdminOrReadOnly] 
    
    def get(self, request, pk=None):
        try:
            if pk:
                quiz = get_object_or_404(Quiz, pk=pk)
                serializer = QuizSerializer(quiz)
                return self.send_successful_response(serializer.data)
            quizzes = Quiz.objects.all()
            serializer = QuizSerializer(quizzes, many=True)
            return self.send_successful_response(serializer.data)
        except Http404:
            return self.send_bad_response(
                {"detail": "Quiz not found."}, status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception("Unexpected error in GET Quiz:")
            return self.send_bad_response(
                {"detail": "An unexpected error occurred."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def post(self, request):
    try:
        serializer = QuizSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.send_201_response(serializer.data)
    except ValidationError as e:
        return self.send_bad_response(e.detail, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("Unexpected error in POST Quiz:")
        return self.send_bad_response(
            {"detail": "An unexpected error occurred."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def put(self, request, pk):
    try:
        quiz = get_object_or_404(Quiz, pk=pk)
        serializer = QuizSerializer(quiz, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.send_successful_response(serializer.data)
    except Http404:
        return self.send_bad_response(
            {"detail": "Quiz not found."}, status_code=status.HTTP_404_NOT_FOUND
        )
    except ValidationError as e:
        return self.send_bad_response(e.detail, status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("Unexpected error in PUT Quiz:")
        return self.send_bad_response(
            {"detail": "An unexpected error occurred."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


    def patch(self, request, pk):
        try:
            quiz = get_object_or_404(Quiz, pk=pk)
            serializer = QuizSerializer(quiz, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.send_successful_response(serializer.data)
        except Http404:
            return self.send_bad_response(
                {"detail": "Quiz not found."}, status_code=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return self.send_bad_response(e.detail, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Unexpected error in PATCH Quiz:")
            return self.send_bad_response(
                {"detail": "An unexpected error occurred."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def delete(self, request, pk):
            try:
                quiz = get_object_or_404(Quiz, pk=pk)
                quiz.delete()
                return self.send_no_content_response()
            except Http404:
                return self.send_bad_response({"detail": "Quiz not found."}, status_code=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.exception("Unexpected error on DELETE Quiz:")
                return self.send_bad_response({"detail": "An unexpected error occurred."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@extend_schema(tags=['Participation', 'Answer'])
class AnswerAPIView(ParticipationBaseView):
    serializer_class = AnswerSerializer
    permission_classes = [AnswerPermission]

    def get(self, request, pk=None):
        try:
            if pk:
                answer = get_object_or_404(Answer, pk=pk)
                serializer = AnswerSerializer(answer)
                return self.send_successful_response(serializer.data)
            answers = Answer.objects.all()
            serializer = AnswerSerializer(answers, many=True)
            return self.send_successful_response(serializer.data)
        except Http404:
            return self.send_bad_response(
                {"detail": "Answer not found."}, status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception("Unexpected error in GET Answer:")
            return self.send_bad_response(
                {"detail": "An unexpected error occurred."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            serializer = AnswerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.send_201_response(serializer.data)
        except ValidationError as e:
            return self.send_bad_response(e.detail, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Unexpected error in POST Answer:")
            return self.send_bad_response(
                {"detail": "An unexpected error occurred."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        try:
            answer = get_object_or_404(Answer, pk=pk)
            serializer = AnswerSerializer(answer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.send_successful_response(serializer.data)
        except Http404:
            return self.send_bad_response(
                {"detail": "Answer not found."}, status_code=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return self.send_bad_response(e.detail, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Unexpected error in PUT Answer:")
            return self.send_bad_response(
                {"detail": "An unexpected error occurred."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request, pk):
        try:
            answer = get_object_or_404(Answer, pk=pk)
            serializer = AnswerSerializer(answer, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.send_successful_response(serializer.data)
        except Http404:
            return self.send_bad_response(
                {"detail": "Answer not found."}, status_code=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return self.send_bad_response(e.detail, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Unexpected error in PATCH Answer:")
            return self.send_bad_response(
                {"detail": "An unexpected error occurred."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            answer = get_object_or_404(Answer, pk=pk)
            answer.delete()
            return self.send_no_content_response()
        except Http404:
            return self.send_bad_response(
                {"detail": "Answer not found."}, status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception("Unexpected error in DELETE Answer:")
            return self.send_bad_response(
                {"detail": "An unexpected error occurred."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

@extend_schema(tags=['Participation', 'Score'])
class ScoreAPIView(ParticipationBaseView):
    permission_classes = [IsAdminOrTeacher]
    serializer_class = ScoreSerializer
    def get(self, request, pk=None):
        if pk:
            score = get_object_or_404(Score, pk=pk)
            serializer = ScoreSerializer(score)
            return self.send_successful_response(serializer.data)
        scores = Score.objects.all()
        serializer = ScoreSerializer(scores, many=True)
        return self.send_successful_response(serializer.data)

    def post(self, request):
        serializer = ScoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.send_201_response(serializer.data)
        return self.send_bad_response(serializer.errors)

    def put(self, request, pk):
        score = get_object_or_404(Score, pk=pk)
        serializer = ScoreSerializer(score, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.send_successful_response(serializer.data)
        return self.send_bad_response(serializer.errors)

    def patch(self, request, pk):
        score = get_object_or_404(Score, pk=pk)
        serializer = ScoreSerializer(score, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.send_successful_response(serializer.data)
        return self.send_bad_response(serializer.errors)

    def delete(self, request, pk):
        score = get_object_or_404(Score, pk=pk)
        score.delete()
        return self.send_no_content_response()

@extend_schema(tags=['Participation', 'Task'])
class TaskAPIView(ParticipationBaseView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TaskSerializer
    def get(self, request, pk=None):
        if pk:
            task = get_object_or_404(Task, pk=pk)
            serializer = TaskSerializer(task)
            return self.send_successful_response(serializer.data)
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return self.send_successful_response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.send_201_response(serializer.data)
        return self.send_bad_response(serializer.errors)

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.send_successful_response(serializer.data)
        return self.send_bad_response(serializer.errors)

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.send_successful_response(serializer.data)
        return self.send_bad_response(serializer.errors)

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        task.delete()
        return self.send_no_content_response()
