from rest_framework import serializers
from .models import *


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        lookup_field = 'id'

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'
        
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
        lookup_field = 'id'

class AssignTeacherToQuizSerializer(serializers.Serializer):
    quiz_id = serializers.UUIDField()
    teacher_id = serializers.UUIDField()

class QuestionCSVUploadSerializer(serializers.Serializer):
    subject_id = serializers.UUIDField()
    file = serializers.FileField()