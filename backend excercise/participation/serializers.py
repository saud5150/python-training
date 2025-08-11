from django.apps import apps
from rest_framework import serializers
from participation.models import *
class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

    def create(self, validated_data):
        # Automatically set the total questions and total correct based on the quiz
        quiz_instance = validated_data['quiz_id']
        validated_data['total_questions'] = quiz_instance.question_set.count()
        return super().create(validated_data)

    def update(self, instance, validated_data):

        if 'quiz_id' in validated_data:
            quiz_instance = validated_data['quiz_id']
        else:
            quiz_instance = instance.quiz_id
        
        validated_data['total_questions'] = quiz_instance.question_set.count()
        return super().update(instance, validated_data)

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'user_quiz_id', 'question_id', 'answer_text', 'is_correct']
        read_only_fields = ['is_correct']  # disallow client to set this directly

    def create(self, validated_data):
        answer_text = validated_data.get('answer_text')
        question = validated_data.get('question_id')
        correct_answer = getattr(question, 'correct_answer', None)
        if answer_text and correct_answer:
            is_correct = answer_text.strip().lower() == correct_answer.strip().lower()
        else:
            is_correct = False
        validated_data['is_correct'] = is_correct
        answer = super().create(validated_data)
        self.update_total_correct(answer.user_quiz_id)
        self.update_participation_score(answer.user_quiz_id)
        self.update_total_correct(answer.user_quiz_id)
        self.update_participation_score(answer.user_quiz_id)
        return answer

    def update_total_correct(self, user_quiz_id):
            """Helper method to update total_correct on participation"""
            QuizParticipation = apps.get_model('participation', 'Quiz')  # adjust as needed
            try:
                participation = QuizParticipation.objects.get(id=user_quiz_id.id)
            except QuizParticipation.DoesNotExist:
                return

            # Count all correct answers for this participation
            total_correct_count = Answer.objects.filter(
                user_quiz_id=participation,
                is_correct=True
            ).count()

            participation.total_correct = total_correct_count
            participation.save(update_fields=['total_correct'])

    def update_participation_score(self, participation):
            # Calculate total_correct and total_questions
            Answer = apps.get_model('participation', 'Answer')  # Adjust app/model names
            total_correct = Answer.objects.filter(user_quiz_id=participation, is_correct=True).count()
            total_questions = Answer.objects.filter(user_quiz_id=participation).count()
                    # Update participation fields and save (which recalculates score)
            participation.total_correct = total_correct
            participation.total_questions = total_questions
            participation.score = round(total_correct / total_questions, 4) if total_questions > 0 else 0
            participation.save()

    def update(self, instance, validated_data):
        answer = super().update(instance, validated_data)
        self.update_total_correct(answer.user_quiz_id)
        self.update_participation_score(answer.user_quiz_id)
        return answer

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = '__all__'
        lookup_field = 'id'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__' 
        lookup_field = 'id'