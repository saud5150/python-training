from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
import csv
from io import TextIOWrapper
from base_model import BaseModel
from users.models import User
from django.apps import apps

class Subject(BaseModel):
    name = models.CharField(max_length=100)
    teachers = models.ManyToManyField(User, limit_choices_to={'role': 'teacher'}, related_name='subjects', blank=True)

    def __str__(self):
        return self.name

class Quiz(BaseModel):
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    assigned_teacher = models.ForeignKey(User, limit_choices_to={'role': 'teacher'}, related_name='quizzes', on_delete=models.SET_NULL , null = True)

    def __str__(self):
        return self.title
    

class Question(BaseModel):
    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.TextField()
    correct_answer = models.TextField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Dynamically get participation model to avoid circular import
        QuizParticipation = apps.get_model('participation', 'Quiz')  # adjust 'Quiz' to your participation model name
        
        participations = QuizParticipation.objects.filter(quiz_id=self.quiz_id)
        count = self.quiz_id.question_set.count()
        for participation in participations:
            participation.total_questions = count
            participation.save(update_fields=['total_questions'])  

    def __str__(self):
        return f"Q: {self.question_text[:50]}..."
