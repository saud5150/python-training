from rest_framework import viewsets, permissions
from rest_framework.generics import GenericAPIView

from quiz.models import Question, Quiz, Subject
from .models import *
from .serializers import *

from django.shortcuts import render
from rest_framework import viewsets, permissions

from quiz.serializers import QuestionSerializer, QuizSerializer, SubjectSerializer
from users.permissions import IsAdmin, IsTeacher, IsAdminOrTeacher

# Create your views here.

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]  # Only admin/teacher can create/edit
        return [permissions.IsAuthenticated()]  # Anyone can view

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [permissions.IsAuthenticated()]

class QuestionCSVUploadView(GenericAPIView):
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser]
    serializer_class = QuestionCSVUploadSerializer  # <-- Add this

    def post(self, request, format=None):
        subject_id = request.data.get('Subject_ID')
        if not subject_id:
            return Response({'error': 'subject_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            subject = Subject.objects.get(Subject_ID=subject_id)
        except Subject.DoesNotExist:
            return Response({'error': f'Subject with id {subject_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        from datetime import datetime
        quiz_title = f"Uploaded Quiz {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        quiz = Quiz.objects.create(Title=quiz_title, Description="Bulk uploaded via CSV", Subject_ID=subject)

        file_obj = request.FILES.get('file')
        if not file_obj:
            quiz.delete()
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
        decoded_file = TextIOWrapper(file_obj, encoding='utf-8')
        reader = csv.DictReader(decoded_file)
        # Check columns
        if reader.fieldnames != ['question', 'answer']:
            quiz.delete()
            return Response({'error': 'CSV must have columns: question, answer'}, status=status.HTTP_400_BAD_REQUEST)
        questions = []
        errors = []
        for idx, row in enumerate(reader, start=2):  # start=2 for header row
            question_text = row.get('question', '').strip()
            answer_text = row.get('answer', '').strip()
            if not question_text or not answer_text:
                errors.append(f"Row {idx}: Both question and answer must be filled.")
            else:
                questions.append(Question(Question_Text=question_text, Correct_Answer=answer_text, Quiz_ID=quiz))
        if errors:
            quiz.delete()
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        Question.objects.bulk_create(questions)
        return Response({'status': 'success', 'inserted': len(questions), 'quiz_id': str(quiz.Quiz_ID), 'quiz_title': quiz.Title, 'subject_id': str(subject.Subject_ID), 'subject_name': subject.Name})
