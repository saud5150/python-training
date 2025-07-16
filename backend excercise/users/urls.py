from django.urls import path
from .views import StudentRegistrationView, TeacherRegistrationView, AdminRegistrationView

urlpatterns = [
    path('register/student/', StudentRegistrationView.as_view(), name='register-student'),
    path('register/teacher/', TeacherRegistrationView.as_view(), name='register-teacher'),
    path('register/admin/', AdminRegistrationView.as_view(), name='register-admin'),
] 