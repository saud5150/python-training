from rest_framework import routers
from django.urls import path, include
from .views import (
    StudentRegistrationView,
    TeacherRegistrationView,
    AdminRegistrationView,
    UserProfileView,
    UserListView,
    UserDetailView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import GoogleLogin

# DRF router for ViewSet routing
# router = routers.DefaultRouter()
# router.register(r'users', UserViewSet)

urlpatterns = [
    # Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

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
