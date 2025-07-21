
from smtplib import SMTPAuthenticationError, SMTPException
from django.forms import ValidationError
from rest_framework import serializers
from users.models import *
from django.core.mail import send_mail
from django.conf import settings

from users.utils import send_registration_email


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
        # Send welcome email after user is created
        # 📨 Email sent from utility
        if not send_registration_email(user, password):
            raise ValidationError({"email": "Failed to send confirmation email. Please contact support."})
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
        """
        Return all fields for all user roles.
        """
        return super().to_representation(instance)
