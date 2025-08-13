from venv import logger
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from base_view import BaseView
from participation.answer.models import Answer
from participation.quiz.models import Quiz
from participation.score.models import Score
from participation.permissions import AnswerPermission, IsAdminOrReadOnly, IsAdminOrReadUpdate
from participation.answer.serializers import AnswerSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.db.models import Sum, Count
from quiz.models import Question
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
# Create your views here.

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