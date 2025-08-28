from venv import logger
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from base_view import BaseView
from participation.answer.models import Answer
from participation.quiz.models import Quiz
from participation.score.models import Score
from participation.permissions import AnswerPermission, IsAdminOrReadOnly, IsAdminOrReadUpdate
from participation.answer.serializers import AnswerSerializer
from participation.filters import AnswerFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.db.models import Sum, Count
from quiz.models import Question
from django.utils import timezone
# Create your views here.

@extend_schema(
    tags=['Participation/ Answer'],
    parameters=[
        OpenApiParameter('user_quiz_id', OpenApiTypes.UUID, description='Filter by user-quiz ID'),
        OpenApiParameter('question_id', OpenApiTypes.UUID, description='Filter by question ID'),
        OpenApiParameter('user_id', OpenApiTypes.UUID, description='Filter by user ID'),
        OpenApiParameter('quiz_id', OpenApiTypes.UUID, description='Filter by quiz ID'),
        OpenApiParameter('subject_id', OpenApiTypes.UUID, description='Filter by subject ID'),
        OpenApiParameter('is_correct', OpenApiTypes.BOOL, description='Filter by answer correctness'),
        OpenApiParameter('answer_text', OpenApiTypes.STR, description='Filter by answer text content (contains)'),
        OpenApiParameter('created_after', OpenApiTypes.DATETIME, description='Filter by creation date (after)'),
        OpenApiParameter('created_before', OpenApiTypes.DATETIME, description='Filter by creation date (before)'),
        OpenApiParameter('ordering', OpenApiTypes.STR, description='Order by: created_at, -created_at, user_quiz_id__score, -user_quiz_id__score'),
        OpenApiParameter('search', OpenApiTypes.STR, description='Search in answer text'),
        OpenApiParameter('page', OpenApiTypes.INT, description='Page number for pagination'),
        OpenApiParameter('page_size', OpenApiTypes.INT, description='Number of items per page (default 20, max 100)'),
    ]
)
class AnswerAPIView(BaseView):
    serializer_class = AnswerSerializer
    permission_classes = [AnswerPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = AnswerFilter
    ordering_fields = ['created_at', 'user_quiz_id__score', 'user_quiz_id__user_id__username']
    ordering = ['-created_at']
    search_fields = ['answer_text']

    def get_queryset(self):
        """Filter answers based on user role with optimized queries"""
        user = self.request.user
        base_queryset = Answer.objects.select_related(
            'user_quiz_id__user_id',              # ParticipationQuiz -> User
            'user_quiz_id__quiz_id__subject_id',  # ParticipationQuiz -> Quiz -> Subject
            'question_id'                         # Answer -> Question
        )
        if user.role in ['admin', 'teacher']:
            return base_queryset.all()
        elif user.role == 'student':
            # Students can only see their own answers
            return base_queryset.filter(user_quiz_id__user_id=user)
        return Answer.objects.none()

    def get(self, request, pk=None):
        try:
            if pk:
                answer = get_object_or_404(self.get_queryset(), pk=pk)
                return self.send_successful_response(
                    answer, 
                    description="Answer retrieved successfully",
                    serializer_class=AnswerSerializer
                )
            
            queryset = self.get_queryset()
            # filtered_queryset = self.apply_filters(queryset, request)
            for backend in self.filter_backends:
                queryset = backend().filter_queryset(request, queryset, self)
            return self.send_successful_response(
                data=queryset,
                description="Answers retrieved successfully",
                serializer_class=AnswerSerializer,
                paginate=True
            )
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
            user_quiz_id_val = request.data.get('user_quiz_id')
            answers_data = request.data.get('answers')
            
            if not user_quiz_id_val:
                return self.send_bad_response({'detail': 'user_quiz_id is required.'}, status_code=status.HTTP_400_BAD_REQUEST)
            
            if not answers_data:
                return self.send_bad_response({'detail': 'No answers provided.'}, status_code=status.HTTP_400_BAD_REQUEST)

            results = []
            user_quiz_id = None
            for answer_data in answers_data:
                question_id_val = answer_data.get('question_id')
                answer_text_val = answer_data.get('answer_text')
                
                # Check for duplicate
                if Answer.objects.filter(user_quiz_id=user_quiz_id_val, question_id=question_id_val).exists():
                    # Get question text 
                    try:
                        question_obj = Question.objects.get(pk=question_id_val)
                        question_text = getattr(question_obj, 'text', str(question_obj))
                    except Exception:
                        question_text = str(question_id_val)
                    return self.send_bad_response(
                        {'detail': f'Answer already exists for question: "{question_text}" in this quiz.'},
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                # Add user_quiz_id to each answer_data
                complete_answer_data = {
                    'user_quiz_id': user_quiz_id_val,
                    'question_id': question_id_val,
                    'answer_text': answer_text_val
                }
                
                serializer = AnswerSerializer(data=complete_answer_data)
                serializer.is_valid(raise_exception=True)
                answer = serializer.save()
                results.append(serializer.data)
                user_quiz_id = answer.user_quiz_id  # Save for later score update

            # After all answers, update Score for the user/quiz/subject
            if user_quiz_id:
                user = user_quiz_id.user_id
                quiz = user_quiz_id.quiz_id
                subject = quiz.subject_id
                user_quizzes = Quiz.objects.filter(user_id=user, quiz_id__subject_id=subject)
                total_score = user_quizzes.aggregate(total=Sum('score'))['total'] or 0
                Score.objects.update_or_create(
                    user_id=user,
                    subject_id=subject,
                    defaults={'aggregate_score': total_score}
                )

                # --- Set completed_at if all questions answered ---
                # Get total questions for this quiz
                total_questions = quiz.questions.count() if hasattr(quiz, 'questions') else quiz.question_set.count()
                answered_count = Answer.objects.filter(user_quiz_id=user_quiz_id).count()
                if answered_count == total_questions:
                    user_quiz_id.completed_at = timezone.now()
                    user_quiz_id.save(update_fields=['completed_at'])

            return self.send_201_response({'answers': results})
        except ValidationError as e:
            return self.send_bad_response(e.detail, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Unexpected error in bulk POST Answer:")
            return self.send_bad_response(
                {"detail": "An unexpected error occurred."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        try:
            answer = get_object_or_404(Answer, pk=pk)
            serializer = AnswerSerializer(answer, data=request.data)
            serializer.is_valid(raise_exception=True)
            updated_answer = serializer.save()  # Get the updated instance
            # Pass the model instance, not serializer.data
            return self.send_successful_response(updated_answer, serializer_class=AnswerSerializer)
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
            updated_answer = serializer.save()  # Get the updated instance
            # Pass the model instance, not serializer.data
            return self.send_successful_response(updated_answer, serializer_class=AnswerSerializer)
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