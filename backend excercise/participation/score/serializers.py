from django.apps import apps
from rest_framework import serializers
from participation.score.models import *

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['user_id', 'subject_id', 'aggregate_score']
        lookup_field = 'id'
