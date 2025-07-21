import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from base_model import BaseModel

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)
    
class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    class RoleType(models.TextChoices):
        ADMIN = 'admin', 'Admin / HR'
        TEACHER = 'teacher', "Teacher"
        STUDENT = 'student', 'Student'

    role = models.CharField(max_length=20, choices = RoleType.choices, default = RoleType.STUDENT)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    # def save(self, *args, **kwargs):
    #     if self.password and not self.Password_Hash:
    #         self.set_password(self.password)
    #     super().save(*args, **kwargs)
    @property
    def id(self):
        return self.User_ID