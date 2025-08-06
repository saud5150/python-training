from django.contrib import admin

from participation.models import Quiz, Answer, Score, Task

# Register your models here.

admin.site.register(Quiz)
admin.site.register(Answer)
admin.site.register(Score)
admin.site.register(Task)