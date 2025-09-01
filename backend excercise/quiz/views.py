from rest_framework.serializers import ValidationError
from django.http import Http404
from rest_framework import viewsets, permissions
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from base_view import BaseView
from quiz.filters import QuestionFilter, QuizFilter, SubjectFilter
from quiz.models import Question, Quiz, Subject
from quiz.permissions import IsAdminOrReadOnlyAuthenticated, IsTeacherOrReadOnlyForStudents
from .models import *
from .serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, permissions

from quiz.serializers import QuestionSerializer, QuizSerializer, SubjectSerializer, StudentQuestionSerializer, StudentQuizSerializer
from users.permissions import IsAdmin, IsTeacher, IsAdminOrTeacher
from .utils import process_question_csv_upload
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from drf_spectacular.types import OpenApiTypes

# Create your views here.

# ---- SUBJECT CRUD ----
@extend_schema(
    tags=['Subject'],
    parameters=[
        OpenApiParameter('name', OpenApiTypes.STR, description='Filter by subject name (contains)'),
        OpenApiParameter('created_after', OpenApiTypes.DATETIME, description='Filter by creation date (after)'),
        OpenApiParameter('ordering', OpenApiTypes.STR, description='Order by: name, -name, created_at, -created_at'),
        OpenApiParameter('search', OpenApiTypes.STR, description='Search in name'),
    ]
)
class SubjectView(BaseView):
    serializer_class = SubjectSerializer 
    filterset_class = SubjectFilter
    permission_classes = [IsAdminOrReadOnlyAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    search_fields = ['name', 'description']
    queryset = Subject.objects.prefetch_related('teachers')

    # def get_queryset(self):
    #     """
    #     Optimized queryset to prevent N+1 queries.
        
    #     Before: 6 queries (1 + 1 + 1 + 3 teacher lookups)
    #     After: 3 queries (1 + 1 + 1 with prefetched teachers)
    #     """
    #     # FIX: Use prefetch_related to solve N+1 problem
    #     return Subject.objects.only('id', 'name').prefetch_related(
    #         'teachers'  # This will fetch all teachers in one query
    #     )

    
    def get(self, request, pk=None):
        try:
            if pk:
                subject = get_object_or_404(Subject, pk=pk)
                return self.send_successful_response(
                    subject, 
                    description="Subject retrieved successfully",
                    serializer_class=SubjectSerializer
                )

            # Apply filters manually to avoid BaseView auto-filtering
            #queryset = self.get_queryset()
            # queryset = Subject.objects.all()

            # ✅ Convert to list to avoid additional queries during serialization
            # subjects_list = list(queryset)            
            return self.send_successful_response(
                data=self.queryset,
                description="Subjects retrieved successfully",
                serializer_class=SubjectSerializer,
                paginate=True
            )
        except Http404:
            return self.send_bad_response(
                {'detail': 'Subject not found.'}, 
                status_code=status.HTTP_404_NOT_FOUND
        )
        except Exception as e:
            return self.send_exception_response(e, "Error retrieving subjects")

    def post(self, request):
        try:
            serializer = SubjectSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            subject = serializer.save()
            return self.send_201_response(serializer.data, "Subject created successfully")
        except Exception as e:
            return self.send_exception_response(e, "Error creating subject")

    def put(self, request, pk):
        try:
            subject = get_object_or_404(Subject, pk=pk)
            serializer = SubjectSerializer(subject, data=request.data)
            serializer.is_valid(raise_exception=True)
            updated_subject = serializer.save()
            return self.send_successful_response(
                updated_subject, 
                serializer_class=SubjectSerializer
            )
        except Http404:
            return self.send_bad_response(
                {'detail': 'Subject not found.'}, 
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.send_exception_response(e, "Error updating subject")

    def patch(self, request, pk):
        try:
            subject = get_object_or_404(Subject, pk=pk)
            serializer = SubjectSerializer(subject, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_subject = serializer.save()
            return self.send_successful_response(
                updated_subject, 
                serializer_class=SubjectSerializer
            )
        except Http404:
            return self.send_bad_response(
                {'detail': 'Subject not found.'}, 
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.send_exception_response(e, "Error updating subject")

    def delete(self, request, pk):
        try:
            subject = get_object_or_404(Subject, pk=pk)
            subject.delete()
            return self.send_no_content_response("Subject deleted successfully")
        except Http404:
            return self.send_bad_response(
                {'detail': 'Subject not found.'}, 
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.send_exception_response(e, "Error deleting subject")

@extend_schema(tags=['Quiz'])
class AssignTeacherToQuizView(APIView):
    permission_classes = [IsAdmin]
    serializer_class = AssignTeacherToQuizSerializer  # <-- Add this

    def post(self, request, format=None):
        quiz_id = request.data.get('quiz_id')
        teacher_id = request.data.get('teacher_id')
        if not quiz_id or not teacher_id:
            return Response({'error': 'quiz_id and teacher_id are required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            teacher = User.objects.get(id=teacher_id, role='teacher')
        except User.DoesNotExist:
            return Response({'error': 'Teacher not found.'}, status=status.HTTP_404_NOT_FOUND)
        quiz.assigned_teacher = teacher
        quiz.save()
        serializer = QuizSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ---- QUIZ CRUD ----
@extend_schema(
    tags=['Quiz'],
    parameters=[
        OpenApiParameter('title', OpenApiTypes.STR, description='Filter by quiz title (contains)'),
        OpenApiParameter('title_exact', OpenApiTypes.STR, description='Filter by exact quiz title'),
        OpenApiParameter('subject_id', OpenApiTypes.UUID, description='Filter by subject ID'),
        OpenApiParameter('subject_name', OpenApiTypes.STR, description='Filter by subject name (contains)'),
        OpenApiParameter('created_after', OpenApiTypes.DATETIME, description='Filter by creation date (after)'),
        OpenApiParameter('created_before', OpenApiTypes.DATETIME, description='Filter by creation date (before)'),
        OpenApiParameter('ordering', OpenApiTypes.STR, description='Order by: title, -title, created_at, -created_at, subject_id__name, -subject_id__name'),
        OpenApiParameter('search', OpenApiTypes.STR, description='Search in title and description'),
        OpenApiParameter('page', OpenApiTypes.INT, description='Page number for pagination'),
        OpenApiParameter('page_size', OpenApiTypes.INT, description='Number of items per page (default 20, max 100)'),
    ]
)
class QuizAPIView(BaseView):
    serializer_class = QuizSerializer
    permission_classes = [IsTeacherOrReadOnlyForStudents]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = QuizFilter
    ordering_fields = ['title', 'created_at', 'subject_id__name']
    ordering = ['title']
    search_fields = ['title', 'description']  
    queryset = Quiz.objects.select_related('subject_id', 'assigned_teacher').only(
        'id', 'title', 'description', 'subject_id__id', 'subject_id__name',
        'assigned_teacher__id', 'assigned_teacher__name', 'assigned_teacher__email'
    )

    def get(self, request, pk=None):
        """
        Retrieve a list of quizzes or a specific quiz by ID.
        Supports filtering, pagination, search, and ordering.
        """
        try:                
            if pk:
                # Single quiz retrieval
                quiz = get_object_or_404(self.queryset, pk=pk)
                return self.send_successful_response(
                    quiz, 
                    description="Quiz retrieved successfully",
                    serializer_class=QuizSerializer
                )

            return self.send_successful_response(
                data=self.queryset,
                description="Quizzes retrieved successfully",
                serializer_class=QuizSerializer,
                paginate=True
            )
            
        except Http404:
            return self.send_bad_response(
                {'detail': 'Quiz not found.'}, 
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.send_exception_response(e, "Error retrieving quizzes")

    def post(self, request):
        """Create a new quiz"""
        try:
            serializer = QuizSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            quiz = serializer.save()
            return self.send_201_response(
                serializer.data, 
                "Quiz created successfully"
            )
        except ValidationError as e:
            return self.send_bad_response(
                e.detail, 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return self.send_exception_response(e, "Error creating quiz")

    def patch(self, request, pk):
        """Partially update a quiz"""
        try:
            quiz = get_object_or_404(Quiz, pk=pk)
            serializer = QuizSerializer(quiz, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_quiz = serializer.save()
            return self.send_successful_response(
                updated_quiz, 
                description="Quiz updated successfully",
                serializer_class=QuizSerializer
            )
        except Http404:
            return self.send_bad_response(
                {'detail': 'Quiz not found.'}, 
                status_code=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return self.send_bad_response(
                e.detail, 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return self.send_exception_response(e, "Error updating quiz")


    def put(self, request, pk=None):
        """
        Update an existing quiz by ID (Teacher only).
        """
        try:
            if not pk:
                return self.send_bad_response(
                    {'detail': 'Quiz ID (pk) is required for update.'},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            quiz = get_object_or_404(Quiz, pk=pk)
            serializer = QuizSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return self.send_successful_response(serializer.data, description="Quiz updated successfully")
            return self.send_bad_response(serializer.errors, description="Validation error updating quiz")
        except Http404:
            return Response({'detail': 'Quiz not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return self.send_exception_response(exc, description="An error occurred while updating the quiz")

    def delete(self, request, pk):
        """Delete a quiz"""
        try:
            quiz = get_object_or_404(Quiz, pk=pk)
            quiz_title = quiz.title  # Store for response message
            quiz.delete()
            return self.send_no_content_response(
                f"Quiz '{quiz_title}' deleted successfully"
            )
        except Http404:
            return self.send_bad_response(
                {'detail': 'Quiz not found.'}, 
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.send_exception_response(e, "Error deleting quiz")

# ---- QUESTION CRUD ----
@extend_schema(
    tags=['Question'],
    parameters=[
        OpenApiParameter('quiz_id', OpenApiTypes.UUID, description='Filter by quiz ID'),
        OpenApiParameter('subject_id', OpenApiTypes.UUID, description='Filter by subject ID'),
        OpenApiParameter('question_text', OpenApiTypes.STR, description='Filter by question text (contains)'),
        OpenApiParameter('created_after', OpenApiTypes.DATETIME, description='Filter by creation date (after)'),
        OpenApiParameter('ordering', OpenApiTypes.STR, description='Order by: text, -text, created_at, -created_at'),
        OpenApiParameter('search', OpenApiTypes.STR, description='Search in question text'),
        # Add pagination parameters
        OpenApiParameter('page', OpenApiTypes.INT, description='Page number for pagination'),
        OpenApiParameter('page_size', OpenApiTypes.INT, description='Number of items per page (max 100)'),
    ]
)
class QuestionView(BaseView):
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminOrReadOnlyAuthenticated]  
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = QuestionFilter
    ordering_fields = ['created_at', 'quiz_id__title']
    ordering = ['quiz_id__title', 'question_text']
    search_fields = ['question_text']
    queryset = Question.objects.select_related('quiz_id').all()


    def get(self, request, pk=None):
        try:
            claims = request.auth
            if claims and claims.get('role') == 'student':
                serializer_class = StudentQuestionSerializer
            else:
                serializer_class = QuestionSerializer
                
            if pk:
                question = get_object_or_404(Question, pk=pk)
                return self.send_successful_response(
                    question, 
                    description="Question retrieved successfully",
                    serializer_class=serializer_class
                )
            
            return self.send_successful_response(
                data=self.queryset,
                description="Questions retrieved successfully",
                serializer_class=serializer_class,
                paginate=True
            )
            
        except Http404:
            return self.send_bad_response(
                {'detail': 'Question not found.'},
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.send_exception_response(e, "Error retrieving questions")

    def post(self, request):
        try:
            serializer = QuestionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            question = serializer.save()
            return self.send_201_response(serializer.data, "Question created successfully")
        except Exception as e:
            return self.send_exception_response(e, "Error creating question")

    def put(self, request, pk):
        try:
            question = get_object_or_404(Question, pk=pk)
            serializer = QuestionSerializer(question, data=request.data)
            serializer.is_valid(raise_exception=True)
            updated_question = serializer.save()
            return self.send_successful_response(
                updated_question, 
                serializer_class=QuestionSerializer
            )
        except Http404:
            return self.send_bad_response(
                {'detail': 'Question not found.'},
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.send_exception_response(e, "Error updating question")

    def patch(self, request, pk):
        try:
            question = get_object_or_404(Question, pk=pk)
            serializer = QuestionSerializer(question, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_question = serializer.save()
            return self.send_successful_response(
                updated_question, 
                serializer_class=QuestionSerializer
            )
        except Http404:
            return self.send_bad_response(
                {'detail': 'Question not found.'},
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.send_exception_response(e, "Error updating question")

    def delete(self, request, pk):
        try:
            question = get_object_or_404(Question, pk=pk)
            question.delete()
            return self.send_no_content_response("Question deleted successfully")
        except Http404:
            return self.send_bad_response(
                {'detail': 'Question not found.'},
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.send_exception_response(e, "Error deleting question")  

@extend_schema(
    tags=['Question'],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                },
                'subject_id': {
                    'type': 'string',
                    'description': 'Subject ID'
                },
                'title': {
                    'type': 'string', 
                    'description': 'Quiz title'
                },
                'description': {
                    'type': 'string',
                    'description': 'Quiz description'
                }
            },
            'required': [ 'file', 'subject_id', 'title', 'description']
        }
    }
)
class QuestionCSVUploadView(GenericAPIView):
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser]
    serializer_class = QuestionCSVUploadSerializer

    def post(self, request, format=None):
        return process_question_csv_upload(request)
