from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='User_ID', read_only=True)
    class Meta:
        model = User
        fields = '__all__'
        lookup_field = 'User_ID'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        lookup_field = 'Subject_ID'

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'
        lookup_field = 'Quiz_ID'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
        lookup_field = 'Question_ID'

class UserQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuiz
        fields = '__all__'
        lookup_field = 'User_Quiz_ID'

class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = '__all__'
        lookup_field = 'User_Answer_ID'

class UserSubjectScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubjectScore
        fields = '__all__'
        lookup_field = 'User_Subject_Score_ID'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__' 
        lookup_field = 'Task_ID'