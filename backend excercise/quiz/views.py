from django.http import Http404
from rest_framework import viewsets, permissions
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from base_view import BaseView
from quiz.models import Question, Quiz, Subject
from quiz.permissions import IsTeacherOrReadOnlyForStudents
from .models import *
from .serializers import *

from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, permissions

from quiz.serializers import QuestionSerializer, QuizSerializer, SubjectSerializer
from users.permissions import IsAdmin, IsTeacher, IsAdminOrTeacher
from .utils import process_question_csv_upload
from drf_spectacular.utils import extend_schema

# Create your views here.

# ---- SUBJECT CRUD ----
@extend_schema(tags=['Subject'])
class SubjectView(APIView):
    serializer_class = SubjectSerializer 

        # We'll determine permission per-method
    def get_permissions(self):
        # Only admin can POST (create), PUT/PATCH (update), DELETE
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAdmin()]
        # All authenticated users can GET (list/retrieve)
        return [permissions.IsAuthenticated()]

    def get(self, request, pk=None):
        if pk is None:
            objs = Subject.objects.all()
            serializer = SubjectSerializer(objs, many=True)
            return Response(serializer.data)
        obj = get_object_or_404(Subject, pk=pk)
        serializer = SubjectSerializer(obj)
        return Response(serializer.data)

    def post(self, request, pk=None):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response(SubjectSerializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        obj = get_object_or_404(Subject, pk=pk)
        serializer = SubjectSerializer(obj, data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response(SubjectSerializer(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        obj = get_object_or_404(Subject, pk=pk)
        serializer = SubjectSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            obj = serializer.save()
            return Response(SubjectSerializer(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        obj = get_object_or_404(Subject, pk=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
@extend_schema(tags=['Quiz'])
class QuizAPIView(BaseView):
    serializer_class = QuizSerializer
    permission_classes = [IsTeacherOrReadOnlyForStudents]
    def get(self, request, pk=None):
        """
        Retrieve a list of quizzes or a specific quiz by ID.
        """
        try:
            if pk is None:
                quizzes = Quiz.objects.all()
                serializer = QuizSerializer(quizzes, many=True)
                return self.send_successful_response(serializer.data, description="List of quizzes retrieved successfully")
            quiz = get_object_or_404(Quiz, pk=pk)
            serializer = QuizSerializer(quiz)
            return self.send_successful_response(serializer.data, description="Quiz retrieved successfully")
        except Http404:
            return Response(
                {'detail': 'Quiz not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return self.send_exception_response(e, "An error occurred while retrieving quizzes")

    
    def post(self, request):
        """
        Create a new quiz (Teacher only).
        """
        try:
            serializer = QuizSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return self.send_201_response(serializer.data, description="Quiz created successfully")
            return self.send_bad_response(serializer.errors, description="Validation error creating quiz")
        except Exception as exc:
            return self.send_exception_response(exc, description="An error occurred while creating the quiz")

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

    def delete(self, request, pk=None):
        """
        Delete a quiz by ID (Teacher only).
        """
        try:
            if not pk:
                return self.send_bad_response(
                    {'detail': 'Quiz ID (pk) is required for deletion.'},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            quiz = get_object_or_404(Quiz, pk=pk)
            quiz.delete()
            return self.send_no_content_response()
        except Http404:
            return Response({'detail': 'Quiz not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return self.send_exception_response(exc, description="An error occurred while deleting the quiz")

# ---- QUESTION CRUD ----
@extend_schema(tags=['Question'])
class QuestionView(APIView):
    serializer_class = QuestionSerializer
        # We'll determine permission per-method
    def get_permissions(self):
        # Only admin can POST (create), PUT/PATCH (update), DELETE
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAdmin()]
        # All authenticated users can GET (list/retrieve)
        return [permissions.IsAuthenticated()]

    def get(self, request, pk=None):
        if pk is None:
            objs = Question.objects.select_related('quiz_id').all()
            serializer = QuestionSerializer(objs, many=True)
            return Response(serializer.data)
        obj = get_object_or_404(Question, pk=pk)
        serializer = QuestionSerializer(obj)
        return Response(serializer.data)

    def post(self, request, pk=None):
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response(QuestionSerializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        obj = get_object_or_404(Question, pk=pk)
        serializer = QuestionSerializer(obj, data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response(QuestionSerializer(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        obj = get_object_or_404(Question, pk=pk)
        serializer = QuestionSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            obj = serializer.save()
            return Response(QuestionSerializer(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        obj = get_object_or_404(Question, pk=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@extend_schema(tags=['Question'])
class QuestionCSVUploadView(GenericAPIView):
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser]
    serializer_class = QuestionCSVUploadSerializer  # <-- Add this

    def post(self, request, format=None):
        return process_question_csv_upload(request)
