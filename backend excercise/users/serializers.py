
from smtplib import SMTPAuthenticationError, SMTPException
from django.forms import ValidationError
from rest_framework import serializers
from users.models import *
from django.core.mail import send_mail
from django.conf import settings


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
        try:
            send_mail(
                subject='Your Account Has Been Created',
                message=f"Hi {user.name}, your account is now active.",
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False
            )
        except SMTPAuthenticationError:
            raise ValidationError({"email": "Email sending failed: Invalid credentials."})
        except SMTPException as e:
            raise ValidationError({"email": f"Email sending failed: {str(e)}"})
        except Exception:
            raise ValidationError({"email": "An unexpected error occurred while sending email."})
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
