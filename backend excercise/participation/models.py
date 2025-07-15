import uuid
from django.db import models

from quizzes.models import Question, Quiz, Subject
from users.models import User

# Create your models here.

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
