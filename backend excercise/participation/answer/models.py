from django.db import models
from base_model import BaseModel
from quiz.models import Question, Quiz
\
# Create your models here.

class Answer(BaseModel):
    user_quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(null = True)
    is_correct = models.BooleanField(default = False)

    def __str__(self):
        return f"Answer to {self.question_id} by {self.user_quiz_id.user_id}"
