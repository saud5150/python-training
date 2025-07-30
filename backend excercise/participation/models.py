import uuid
from django.db import models

from base_model import BaseModel
from quiz.models import Question, Quiz, Subject
from users.models import User

# Create your models here.

class Quiz(BaseModel):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.DecimalField(null = True, max_digits=5, decimal_places=2)
    total_questions = models.IntegerField()
    total_correct = models.IntegerField()
    completed_at = models.DateTimeField(null = True, blank = True)

    def __str__(self):
        return f"{self.user_id} - {self.quiz_id} ({self.score})"

class Answer(BaseModel):
    user_quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(null = True)
    is_correct = models.BooleanField(default = False)

    def __str__(self):
        return f"Answer to {self.question_id} by {self.user_quiz_id.user_id}"

class Score(BaseModel):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    aggregate_score = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.user_id} - {self.subject_id}: {self.aggregate_score}"

class Task(BaseModel):
    class TaskType(models.TextChoices):
        QUIZ = 'quiz', 'Quiz'
        REMINDER = 'reminder', 'Reminder'
        TODO = 'todo', 'To-Do'

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    user_quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE, null = True, blank = True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    due_date = models.DateTimeField()
    type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.TODO
    )

    def __str__(self):
        return f"{self.title} ({self.status})"
