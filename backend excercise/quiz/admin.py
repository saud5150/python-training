from django.contrib import admin

from quiz.models import Subject, Quiz, Question
from .models import *

admin.site.register(Subject)
admin.site.register(Quiz)
admin.site.register(Question)

