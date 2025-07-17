from django.urls import path
from .views import StudentRegistrationView, TeacherRegistrationView, AdminRegistrationView, UserProfileView, UserDeleteView

urlpatterns = [
    path('register/student/', StudentRegistrationView.as_view(), name='register-student'),
    path('register/teacher/', TeacherRegistrationView.as_view(), name='register-teacher'),
    path('register/admin/', AdminRegistrationView.as_view(), name='register-admin'),
    path('users/me/', UserProfileView.as_view(), name='user-profile'),
    path('users/delete/<uuid:user_id>/', UserDeleteView.as_view(), name='user-delete'),
] 