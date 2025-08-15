from venv import logger
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from base_view import BaseView
from participation.quiz.models import Quiz as ParticipationQuiz
from participation.permissions import AnswerPermission, IsAdminOrReadOnly, IsAdminOrReadUpdate
from participation.quiz.serializers import QuizSerializer
from participation.filters import QuizFilter
from users.permissions import IsAdmin, IsAdminOrTeacher, IsTeacher
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.db.models import Sum, Count
from quiz.models import Question
from django.utils import timezone
# Create your views here.
@extend_schema(
    tags=['Participation/ Quiz'],
    parameters=[
        OpenApiParameter('user_id', OpenApiTypes.UUID, description='Filter by user ID'),
        OpenApiParameter('quiz_id', OpenApiTypes.UUID, description='Filter by assigned quiz ID'),
        OpenApiParameter('subject_id', OpenApiTypes.UUID, description='Filter by subject ID'),
        OpenApiParameter('min_score', OpenApiTypes.NUMBER, description='Minimum score threshold'),
        OpenApiParameter('max_score', OpenApiTypes.NUMBER, description='Maximum score threshold'),
        OpenApiParameter('score', OpenApiTypes.NUMBER, description='Exact score match'),
        OpenApiParameter('min_total_questions', OpenApiTypes.INT, description='Minimum number of questions'),
        OpenApiParameter('min_total_correct', OpenApiTypes.INT, description='Minimum correct answers'),
        OpenApiParameter('completed', OpenApiTypes.BOOL, description='Filter by completion status'),
        OpenApiParameter('created_after', OpenApiTypes.DATETIME, description='Created after this date'),
        OpenApiParameter('created_before', OpenApiTypes.DATETIME, description='Created before this date'),
        OpenApiParameter('completed_after', OpenApiTypes.DATETIME, description='Completed after this date'),
        OpenApiParameter('completed_before', OpenApiTypes.DATETIME, description='Completed before this date'),
        OpenApiParameter('ordering', OpenApiTypes.STR, description='Order by: score, -score, created_at, -created_at, completed_at, -completed_at'),
        OpenApiParameter('search', OpenApiTypes.STR, description='Search in quiz title and user name'),
        OpenApiParameter('page', OpenApiTypes.INT, description='Page number for pagination'),
        OpenApiParameter('page_size', OpenApiTypes.INT, description='Number of items per page (default 20, max 100)'),
    ]
)
class QuizAPIView(BaseView):
    serializer_class = QuizSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = QuizFilter
    ordering_fields = ['score', 'created_at', 'completed_at', 'total_questions', 'total_correct']
    ordering = ['-created_at']
    search_fields = ['quiz_id__title', 'user_id__username', 'user_id__email'] 
    
    def get_queryset(self):
        """Get queryset with optimized database queries"""
        return ParticipationQuiz.objects.select_related(
            'user_id',
            'quiz_id__subject_id'
        ).all()

    def apply_filters(self, queryset, request):
        """Apply filtering, ordering, and search"""
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(request, queryset, self)
        return queryset
    
    def get(self, request, pk=None):
        try:
            if pk:
                quiz = get_object_or_404(self.get_queryset(), pk=pk)
                return self.send_successful_response(
                    quiz, 
                    description="Quiz participation retrieved successfully",
                    serializer_class=QuizSerializer
                )
            
            queryset = self.get_queryset()
            filtered_queryset = self.apply_filters(queryset, request)
            
            return self.send_successful_response(
                data=filtered_queryset,
                description="Quiz participations retrieved successfully",
                serializer_class=QuizSerializer,
                paginate=True
            )
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
            quiz = serializer.save()  # Get the saved instance
            return self.send_201_response(serializer.data)  # This is fine for 201 response
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
            quiz = get_object_or_404(ParticipationQuiz, pk=pk)
            serializer = QuizSerializer(quiz, data=request.data)
            serializer.is_valid(raise_exception=True)
            updated_quiz = serializer.save()  # Get the updated instance
            # Pass the model instance, not serializer.data
            return self.send_successful_response(updated_quiz, serializer_class=QuizSerializer)
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
            quiz = get_object_or_404(ParticipationQuiz, pk=pk)
            serializer = QuizSerializer(quiz, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_quiz = serializer.save()  # Get the updated instance
            # Pass the model instance, not serializer.data
            return self.send_successful_response(updated_quiz, serializer_class=QuizSerializer)
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
            quiz = get_object_or_404(ParticipationQuiz, pk=pk)
            quiz.delete()
            return self.send_no_content_response()
        except Http404:
            return self.send_bad_response({"detail": "Quiz not found."}, status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("Unexpected error on DELETE Quiz:")
            return self.send_bad_response({"detail": "An unexpected error occurred."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

