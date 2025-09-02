from django.apps import apps
from rest_framework import serializers
from participation.quiz.models import *
class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['user_id', 'quiz_id', 'score', 'total_questions', 'total_correct', 'completed_at']

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
