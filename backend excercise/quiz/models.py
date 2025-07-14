import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
import csv
from io import TextIOWrapper

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

class User(AbstractBaseUser, PermissionsMixin):
    User_ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=50)
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

class Subject(models.Model):
    Subject_ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Name = models.CharField(max_length=100)

    def __str__(self):
        return self.Name

class Quiz(models.Model):
    Quiz_ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Subject_ID = models.ForeignKey(Subject, on_delete=models.CASCADE)
    Title = models.CharField(max_length=100)
    Description = models.TextField()

    def __str__(self):
        return self.Title

class Question(models.Model):
    Question_ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Quiz_ID = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    Question_Text = models.TextField()
    Correct_Answer = models.TextField()

    def __str__(self):
        return f"Q: {self.Question_Text[:50]}..."

class UserQuiz(models.Model):
    User_Quiz_Id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    User_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    Quiz_ID = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    Score = models.DecimalField(max_digits=5, decimal_places=2)
    Total_Questions = models.IntegerField()
    Total_Correct = models.IntegerField()
    Started_At = models.DateTimeField()
    Completed_At = models.DateTimeField()

    def __str__(self):
        return f"{self.User_ID} - {self.Quiz_ID} ({self.Score})"

class UserAnswer(models.Model):
    User_Answer_Id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    User_Quiz_ID = models.ForeignKey(UserQuiz, on_delete=models.CASCADE)
    Question_ID = models.ForeignKey(Question, on_delete=models.CASCADE)
    Answer_Text = models.TextField()
    Is_Correct = models.BooleanField()

    def __str__(self):
        return f"Answer to {self.Question_ID} by {self.User_Quiz_ID.User_ID}"

class UserSubjectScore(models.Model):
    User_Subject_Score_ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    User_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    Subject_ID = models.ForeignKey(Subject, on_delete=models.CASCADE)
    Aggregate_Score = models.DecimalField(max_digits=5, decimal_places=2)
    Last_Updated = models.DateTimeField()

    def __str__(self):
        return f"{self.User_ID} - {self.Subject_ID}: {self.Aggregate_Score}"

class Task(models.Model):
    Task_ID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    User_ID = models.ForeignKey(User, on_delete=models.CASCADE)
    User_Quiz_ID = models.ForeignKey(UserQuiz, on_delete=models.CASCADE)
    Title = models.CharField(max_length=50)
    Description = models.CharField(max_length=255)
    Status = models.CharField(max_length=50)
    Created_At = models.DateTimeField()
    Due_date = models.DateTimeField()

    def __str__(self):
        return f"{self.Title} ({self.Status})"

