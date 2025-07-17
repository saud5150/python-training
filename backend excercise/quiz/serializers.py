from rest_framework import serializers

class QuestionCSVUploadSerializer(serializers.Serializer):
    Subject_ID = serializers.UUIDField()
    file = serializers.FileField()