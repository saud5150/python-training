from venv import logger
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from base_view import BaseView
from participation.models import Task, Answer, Quiz, Score
from participation.permissions import AnswerPermission, IsAdminOrReadOnly, IsAdminOrReadUpdate
from participation.serializers import TaskSerializer, AnswerSerializer, QuizSerializer, ScoreSerializer
from users.permissions import IsAdmin, IsAdminOrTeacher, IsTeacher
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.db.models import Sum, Count
from quiz.models import Question
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from participation.filters import ScoreFilter

# Create your views here.
@extend_schema(tags=['Participation/ Quiz'])
class QuizAPIView(BaseView):
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

@extend_schema(tags=['Participation/ Answer'])
class AnswerAPIView(BaseView):
    serializer_class = AnswerSerializer
    permission_classes = [AnswerPermission]

    def get_queryset(self):
        """Filter answers based on user role"""
        user = self.request.user
        if user.role in ['admin', 'teacher']:
            return Answer.objects.all()
        elif user.role == 'student':
            # Students can only see their own answers
            return Answer.objects.filter(user_quiz_id__user_id=user)
        return Answer.objects.none()

    def get(self, request, pk=None):
        try:
            if pk:
                answer = get_object_or_404(self.get_queryset(), pk=pk)
                serializer = AnswerSerializer(answer)
                return self.send_successful_response(serializer.data)
            answers = self.get_queryset()
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

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from participation.filters import ScoreFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes



@extend_schema(tags=['Participation/ Task'])
class TaskAPIView(BaseView):
    permission_classes = [IsAdminOrReadUpdate]
    serializer_class = TaskSerializer
    
    def get(self, request, pk=None):
        try:
            if pk:
                task = get_object_or_404(Task, pk=pk)
                
                serializer = TaskSerializer(task)
                return self.send_successful_response(serializer.data)
            tasks = Task.objects.all()
            serializer = TaskSerializer(tasks, many=True)
            return self.send_successful_response(serializer.data)
        except Http404:
            return Response(
                {'detail': 'Task not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.send_exception_response(e, "An error occurred while retrieving tasks")

    def post(self, request):
        try:
            serializer = TaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.send_201_response(serializer.data)
        except Exception as e:
            return self.send_exception_response(e, "An error occurred while creating the task")

    def put(self, request, pk):
        try:
            task = get_object_or_404(Task, pk=pk)
            serializer = TaskSerializer(task, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return self.send_successful_response(serializer.data)
        except Http404:
            # Explicit 404 handling
            return Response({'detail': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.send_exception_response(e, "An error occurred while updating the task")
        return self.send_bad_response(serializer.errors)

    def patch(self, request, pk):
        try:
            task = get_object_or_404(Task, pk=pk)
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.send_successful_response(serializer.data)
        except Http404:
            # Explicit 404 handling
            return Response({'detail': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.send_exception_response(e, "An error occurred while updating the task")
        return self.send_bad_response(serializer.errors)

    def delete(self, request, pk):
        try:
            task = get_object_or_404(Task, pk=pk)
            task.delete()
        except Http404:
            # Explicit 404 handling
            return Response({'detail': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.send_exception_response(e, "An error occurred while deleting the task")
        return self.send_no_content_response()

@extend_schema(
    tags=['Participation/ Score'],
    parameters=[
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
                OpenApiExample('Highest score first', value='-aggregate_score'),
                OpenApiExample('Lowest score first', value='aggregate_score'),
                OpenApiExample('Newest first', value='-created_at'),
            ]
        ),
       OpenApiParameter(
            name='min_aggregate_score',  # Change this to match standard naming
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
            description='Filter scores with aggregate score >= this value',
            examples=[
                OpenApiExample('Above 50', value=50),
                OpenApiExample('Above 70', value=70),
                OpenApiExample('Above 80', value=80),
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
            
        # Apply ordering
        ordering = request.query_params.get('ordering', '-aggregate_score')
        valid_orderings = ['aggregate_score', '-aggregate_score', 'created_at', '-created_at', 'updated_at', '-updated_at']
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        

        return queryset
    
    def get(self, request, pk=None):
        try:
            if pk:
                score = get_object_or_404(self.get_queryset(), pk=pk)
                serializer = ScoreSerializer(score)
                return self.send_successful_response(serializer.data)
            
            # Apply filters to queryset
            queryset = self.get_queryset()
            filtered_queryset = self.apply_filters(queryset, request)
            
            serializer = ScoreSerializer(filtered_queryset, many=True)
            return self.send_successful_response(serializer.data)
            
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
            serializer.save()
            return self.send_successful_response(serializer.data)
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
            serializer.save()
            return self.send_successful_response(serializer.data)
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
