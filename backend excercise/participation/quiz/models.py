import uuid
from django.db import models
from django.db.models import Avg
from base_model import BaseModel
from quiz.models import Quiz as QuizAssigned
from users.models import User

# Create your models here.

class Quiz(BaseModel):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_id = models.ForeignKey(QuizAssigned, on_delete=models.CASCADE)
    score = models.DecimalField(default = 0, max_digits=5, decimal_places=2)
    total_questions = models.IntegerField(default = 0)
    total_correct = models.IntegerField(default = 0)
    completed_at = models.DateTimeField(null = True, blank = True)

    def save(self, *args, **kwargs):
        if self.total_correct > 0 and self.total_questions > 0:
            self.score = round((self.total_correct / self.total_questions) * 100, 2)
        else:
            self.score = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_id} - {self.quiz_id} ({self.score})"
