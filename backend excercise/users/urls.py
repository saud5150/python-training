from rest_framework import routers
from django.urls import path, include
from .views import (
    StudentRegistrationView,
    TeacherRegistrationView,
    AdminRegistrationView,
    UserProfileView,
    UserDeleteView,  # optionally remove if handled in ViewSet
    UserViewSet
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# DRF router for ViewSet routing
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    # Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Custom registration endpoints
    path('student/register/', StudentRegistrationView.as_view(), name='register-student'),
    path('teacher/register/', TeacherRegistrationView.as_view(), name='register-teacher'),
    path('admin/register/', AdminRegistrationView.as_view(), name='register-admin'),

    # Profile
    path('profile/', UserProfileView.as_view(), name='profile'),

    # User actions
    path('users/delete/<uuid:user_id>/', UserDeleteView.as_view(), name='user-delete'),  # Optional if ViewSet handles delete

    # Include DRF router URLs for UserViewSet
    path('', include(router.urls)),
]
