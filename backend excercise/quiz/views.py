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

class QuestionCSVUploadView(APIView):
    parser_classes = [MultiPartParser]

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
