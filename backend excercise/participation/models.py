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
    total_questions = models.IntegerField(null = True, blank = True)
    total_correct = models.IntegerField(default = 0)
    completed_at = models.DateTimeField(null = True, blank = True)

    def save(self, *args, **kwargs):
        if self.total_questions and self.total_correct is not None and self.total_questions > 0:
            self.score = round((self.total_correct / self.total_questions) * 100, 2)
        else:
            self.score = None
        super().save(*args, **kwargs)

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

    def save(self, *args, **kwargs):
        # Example: aggregate all quiz scores for this user and subject
        from django.db.models import Sum
        quizzes = Quiz.objects.filter(user_id=self.user_id, quiz_id__subject_id=self.subject_id)
        total_score = quizzes.aggregate(total=Sum('score'))['total'] or 0
        self.aggregate_score = total_score
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.user_id} - {self.subject_id}: {self.aggregate_score}"
    
 
class Task(BaseModel):
    class TaskType(models.TextChoices):
        QUIZ = 'quiz', 'Quiz'
        REMINDER = 'reminder', 'Reminder'
        TODO = 'todo', 'To-Do'

    class TaskStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'            # Task created, not started yet
        IN_PROGRESS = 'in_progress', 'In Progress' # Work ongoing
        COMPLETED = 'completed', 'Completed'      # Task is finished
        OVERDUE = 'overdue', 'Overdue'            # Due date passed, not completed
        CANCELLED = 'cancelled', 'Cancelled'      # Task was cancelled/removed

    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=uuid.uuid4)
    user_quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE, null = True, blank = True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=20,
                              choices=TaskStatus.choices,
                              default=TaskStatus.PENDING)
    due_date = models.DateTimeField()
    type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.TODO
    )

    def __str__(self):
        return f"{self.title} ({self.status})"
