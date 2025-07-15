import uuid
from django.db import models

# Create your models here.
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
