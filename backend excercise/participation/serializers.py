from rest_framework import serializers
from .models import *

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