import uuid
from django.db import models
from django.db.models import Avg
from base_model import BaseModel
from quiz.models import Quiz, Subject
from users.models import User

# Create your models here.

class Score(BaseModel):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    aggregate_score = models.DecimalField(max_digits=5, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calculate AVERAGE score, not SUM
        quizzes = Quiz.objects.filter(
            user_id=self.user_id, 
            quiz_id__subject_id=self.subject_id
        )
        
        if quizzes.exists():
            avg_score = quizzes.aggregate(avg=Avg('score'))['avg'] or 0
            self.aggregate_score = round(avg_score, 2)
            #self.aggregate_score = quizzes.aggregate(total=Avg('score'))['total'] or 0
        else:
            self.aggregate_score = 0
            
        super().save(*args, **kwargs)

    def update_aggregate_score(self):
        """Call this method when quiz scores change"""
        # Don't trigger save() recursion - use update_fields
        from django.db.models import Avg
        quizzes = Quiz.objects.filter(
            user_id=self.user_id, 
            quiz_id__subject_id=self.subject_id
        )
        
        if quizzes.exists():
            avg_score = quizzes.aggregate(avg=Avg('score'))['avg'] or 0
            self.aggregate_score = round(avg_score, 2)
        else:
            self.aggregate_score = 0
            
        # Use update_fields to avoid triggering save() again
        super().save(update_fields=['aggregate_score'])
 