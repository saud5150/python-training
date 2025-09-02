from rest_framework import serializers
from .models import *


# class SubjectSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subject
#         fields = '__all__'
#         lookup_field = 'id'

# In quiz/serializers.py
class SubjectSerializer(serializers.ModelSerializer):
    # ✅ Use SerializerMethodField to avoid extra queries
    teachers = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'teachers']
    
    def get_teachers(self, obj):
        return [
            {
                'id': str(teacher.id),
                'name': teacher.name,
                'email': teacher.email
            }
            for teacher in obj.teachers.all()
        ]

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'correct_answer', 'quiz_id']
        lookup_field = 'id'

class StudentQuestionSerializer(serializers.ModelSerializer):
    """Question serializer for students - excludes correct_answer"""
    class Meta:
        model = Question
        # exclude = ['correct_answer']
        fields = ['id', 'question_text', 'quiz_id']
        lookup_field = 'id'

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'subject_id']

class AssignTeacherToQuizSerializer(serializers.Serializer):
    quiz_id = serializers.UUIDField()
    teacher_id = serializers.UUIDField()

class QuestionCSVUploadSerializer(serializers.Serializer):
    subject_id = serializers.UUIDField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500)
    file = serializers.FileField()