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
        # validated_data['total_correct'] = quiz_instance.total_correct
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

    def validate(self, data):
        answer_text = data.get('answer_text')
        question = data.get('question_id')

        # Fetch the correct answer from the question model
        correct_answer = getattr(question, 'correct_answer', None)

        if answer_text and correct_answer:
            is_correct = answer_text.strip().lower() == correct_answer.strip().lower()
        else:
            is_correct = False

        # Inject the computed value into validated_data
        data['is_correct'] = is_correct
        return data


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