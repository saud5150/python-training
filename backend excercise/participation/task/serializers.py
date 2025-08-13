from django.apps import apps
from rest_framework import serializers
from participation.task.models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__' 
        lookup_field = 'id'