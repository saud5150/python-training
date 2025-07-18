
from rest_framework import serializers
from users.models import *


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='User_ID', read_only=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = '__all__'
        lookup_field = 'User_ID'

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # This hashes the password!
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # This hashes the password!
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user_role = getattr(getattr(request, 'user', None), 'role', None) if request else None

        if user_role == 'student':
            # Students see only id, name, and role
            return {
                'id': data['id'],
                'name': data['name'],
                'role': data['role'],
            }
        elif user_role == 'teacher':
            # Teachers see id, name, role, and email
            return {
                'id': data['id'],
                'name': data['name'],
                'role': data['role'],
                'email': data['email'],
            }
        # Admins and others see all fields
        return data