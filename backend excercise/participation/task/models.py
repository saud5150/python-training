import uuid
from django.db import models
from base_model import BaseModel
from quiz.models import Quiz
from users.models import User
# Create your models here.
 
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
