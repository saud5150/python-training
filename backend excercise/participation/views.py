from venv import logger
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from base_view import BaseView
from participation.models import Task, Answer, Quiz, Score
from participation.permissions import AnswerPermission, IsAdminOrReadOnly, IsAdminOrReadUpdate
from participation.serializers import TaskSerializer, AnswerSerializer, QuizSerializer, ScoreSerializer
from users.permissions import IsAdmin, IsAdminOrTeacher, IsTeacher
from drf_spectacular.utils import extend_schema
from django.db.models import Sum, Count
from quiz.models import Question
from django.utils import timezone

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
            answers_data = request.data.get('answers')
            if not answers_data:
                return self.send_bad_response({'detail': 'No answers provided.'}, status_code=status.HTTP_400_BAD_REQUEST)

            results = []
            user_quiz_id = None
            for answer_data in answers_data:
                user_quiz_id_val = answer_data.get('user_quiz_id')
                question_id_val = answer_data.get('question_id')
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
                serializer = AnswerSerializer(data=answer_data)
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

@extend_schema(tags=['Participation/ Score'])
class ScoreAPIView(BaseView):
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
