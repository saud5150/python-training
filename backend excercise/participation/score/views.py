from venv import logger
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from base_view import BaseView
from participation.task.models import Task
from participation.answer.models import Answer
from participation.quiz.models import Quiz
from participation.score.models import Score
from participation.permissions import AnswerPermission, IsAdminOrReadOnly, IsAdminOrReadUpdate
from participation.score.serializers import ScoreSerializer
from users.permissions import IsAdmin, IsAdminOrTeacher, IsTeacher
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.db.models import Sum, Count
from quiz.models import Question
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
# Create your views here.

@extend_schema(
    tags=['Participation/ Score'],
    parameters=[
        *BaseView.get_pagination_openapi_parameters(),  # Add pagination params
        OpenApiParameter(
            name='subject_id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
            description='Filter by subject UUID',
        ),
        OpenApiParameter(
            name='ordering',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Order by field. Use "-" prefix for descending order',
            examples=[
                OpenApiExample(name='highest_score_first', summary='Highest score first', value='-aggregate_score'),
                OpenApiExample(name='lowest_score_first', summary='Lowest score first', value='aggregate_score'),
                OpenApiExample(name='newest_first', summary='Newest first', value='-created_at'),
            ]
        ),
       OpenApiParameter(
            name='min_aggregate_score',  # Change this to match standard naming
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
            description='Filter scores with aggregate score >= this value',
            examples=[
                OpenApiExample(name='above_50', summary='Above 50', value=50),
                OpenApiExample(name='above_70', summary='Above 70', value=70),
                OpenApiExample(name='above_80', summary='Above 80', value=80),
            ]
        ),
        OpenApiParameter(
            name='max_aggregate_score',  # Change this to match standard naming
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
            description='Filter scores with aggregate score <= this value',
            examples=[
                OpenApiExample(name='below_50', summary='Below 50', value=50),
                OpenApiExample(name='below_70', summary='Below 70', value=70),
                OpenApiExample(name='below_80', summary='Below 80', value=80),
            ]
        ),
    ]
)
class ScoreAPIView(BaseView):
    permission_classes = [IsAdminOrTeacher]
    serializer_class = ScoreSerializer
    
    def get_queryset(self):
        """Filter scores based on user role"""
        user = self.request.user
        if user.role in ['admin', 'teacher']:
            return Score.objects.select_related('user_id', 'subject_id').all()
        elif user.role == 'student':
            return Score.objects.select_related('user_id', 'subject_id').filter(user_id=user)
        return Score.objects.none()
    
    def apply_filters(self, queryset, request):
        """Apply simple filters to queryset"""
        
        # Filter by subject
        subject_id = request.query_params.get('subject_id')
        if subject_id:
            try:
                queryset = queryset.filter(subject_id=subject_id)
            except (ValueError, TypeError):
                # Invalid UUID, ignore filter
                pass
            
        # Filter by minimum score
        min_score = request.query_params.get('min_aggregate_score')
        if min_score:
            try:
                min_score_value = float(min_score)
                queryset = queryset.filter(aggregate_score__gte=min_score_value)
            except (ValueError, TypeError):
                # Invalid score, ignore filter
                pass

        # Filter by maximum score
        max_score = request.query_params.get('max_aggregate_score')
        if max_score:
            try:
                max_score_value = float(max_score)
                queryset = queryset.filter(aggregate_score__lte=max_score_value)
            except (ValueError, TypeError):
                # Invalid score, ignore filter
                pass

        # Apply ordering
        ordering = request.query_params.get('ordering', '-aggregate_score')
        valid_orderings = ['aggregate_score', '-aggregate_score', 'created_at', '-created_at', 'updated_at', '-updated_at']
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        

        return queryset
    
    def get(self, request, pk=None):
        try:
            if pk:
                # Single object - no pagination needed
                score = get_object_or_404(self.get_queryset(), pk=pk)
                return self.send_successful_response(score, "Score retrieved successfully", serializer_class=ScoreSerializer)
            
            # List view - apply filters and pagination
            queryset = self.get_queryset()
            filtered_queryset = self.apply_filters(queryset, request)
            
            # Debug: Check if there are any scores
            print(f"Total scores in queryset: {filtered_queryset.count()}")
            
            # Use BaseView pagination with the correct parameter name
            return self.send_successful_response(
                data=filtered_queryset,  # Pass the queryset as data
                description="Scores retrieved successfully",
                serializer_class=ScoreSerializer,
                paginate=True  # Enable pagination
            )
            
        except Http404:
            return self.send_bad_response(
                {"detail": "Score not found."}, status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception("Unexpected error in GET Score:")
            return self.send_bad_response(
                {"detail": "An unexpected error occurred."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            serializer = ScoreSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.send_201_response(serializer.data)
        except ValidationError as e:
            return self.send_bad_response(e.detail, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Unexpected error in POST Score:")
            return self.send_bad_response(
                {"detail": "An unexpected error occurred."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        try:
            score = get_object_or_404(self.get_queryset(), pk=pk)
            serializer = ScoreSerializer(score, data=request.data)
            serializer.is_valid(raise_exception=True)
            updated_score = serializer.save()
            return self.send_successful_response(updated_score, serializer_class=ScoreSerializer)
        except Http404:
            return self.send_bad_response(
                {"detail": "Score not found."}, status_code=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return self.send_bad_response(e.detail, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Unexpected error in PUT Score:")
            return self.send_bad_response(
                {"detail": "An unexpected error occurred."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request, pk):
        try:
            score = get_object_or_404(self.get_queryset(), pk=pk)
            serializer = ScoreSerializer(score, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_score = serializer.save()
            return self.send_successful_response(updated_score, serializer_class=ScoreSerializer)
        except Http404:
            return self.send_bad_response(
                {"detail": "Score not found."}, status_code=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return self.send_bad_response(e.detail, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Unexpected error in PATCH Score:")
            return self.send_bad_response(
                {"detail": "An unexpected error occurred."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            score = get_object_or_404(self.get_queryset(), pk=pk)
            score.delete()
            return self.send_no_content_response()
        except Http404:
            return self.send_bad_response(
                {"detail": "Score not found."}, status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception("Unexpected error in DELETE Score:")
            return self.send_bad_response(
                {"detail": "An unexpected error occurred."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
