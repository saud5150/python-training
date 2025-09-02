from django.apps import apps
from rest_framework import serializers
from participation.task.models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'type', 'status', 'due_date', 'created_at'] 
        lookup_field = 'id'