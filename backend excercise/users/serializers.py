
from rest_framework import serializers
from users.models import *


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='User_ID', read_only=True)
    class Meta:
        model = User
        fields = '__all__'
        lookup_field = 'User_ID'