from rest_framework import serializers
from .models import *


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        lookup_field = 'id'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
        lookup_field = 'id'

class StudentQuestionSerializer(serializers.ModelSerializer):
    """Question serializer for students - excludes correct_answer"""
    class Meta:
        model = Question
        exclude = ['correct_answer']
        lookup_field = 'id'

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class StudentQuizSerializer(serializers.ModelSerializer):
    """Quiz serializer for students - includes questions without correct answers"""
    questions = StudentQuestionSerializer(source='question_set', many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = '__all__'

class AssignTeacherToQuizSerializer(serializers.Serializer):
    quiz_id = serializers.UUIDField()
    teacher_id = serializers.UUIDField()

class QuestionCSVUploadSerializer(serializers.Serializer):
    subject_id = serializers.UUIDField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500)
    file = serializers.FileField()