from django.contrib import admin

from participation.models import Task, UserAnswer, UserQuiz, UserSubjectScore
from quizzes.models import Question, Quiz, Subject
from users.models import User
from .models import *

admin.site.register(User)
admin.site.register(Subject)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(UserQuiz)
admin.site.register(UserAnswer)
admin.site.register(UserSubjectScore)
admin.site.register(Task)
