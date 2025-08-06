from django.urls import path, include
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    SessionToJWTView,
    StudentRegistrationView,
    TeacherRegistrationView,
    AdminRegistrationView,
    UserProfileView,
    UserListView,
    UserDetailView,
    GoogleLogin
)

urlpatterns = [
    # Token endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    path('accounts/', include('allauth.urls')),
    path('auth/session-to-jwt/', SessionToJWTView.as_view(), name='session_to_jwt'),

    # Authentication endpoints
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),

    # Custom registration endpoints
    path('student/register/', StudentRegistrationView.as_view(), name='register-student'),
    path('teacher/register/', TeacherRegistrationView.as_view(), name='register-teacher'),
    path('admin/register/', AdminRegistrationView.as_view(), name='register-admin'),

    # Profile
    path('profile/', UserProfileView.as_view(), name='profile'),

    # User actions
    path('<uuid:id>/', UserDetailView.as_view(), name='user-detail'),
    path('', UserListView.as_view(), name='user-list-create'),
]
