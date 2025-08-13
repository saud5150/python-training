from django.apps import apps
from rest_framework import serializers
from participation.score.models import *

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = '__all__'
        lookup_field = 'id'
