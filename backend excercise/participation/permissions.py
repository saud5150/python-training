from rest_framework.permissions import BasePermission, SAFE_METHODS

SAFE_METHODS_TASK = ('GET', 'PATCH')

class IsAdminOrReadOnly(BasePermission):
    """
    The request is permitted if:
    - The method is safe (GET, HEAD, OPTIONS) and user is authenticated
    - Or the user is an admin (for DELETE and other unsafe methods)
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # For unsafe methods: require admin
        return request.user and request.user.is_authenticated and request.user.role == 'admin'
from rest_framework.permissions import BasePermission, SAFE_METHODS

class AnswerPermission(BasePermission):
    """
    - Admins and Teachers can do any operation.
    - Students can POST their own answers and GET (view) their own answers.
    - Students cannot update or delete answers.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role in ['admin', 'teacher']:
            return True  # full CRUD

        if user.role == 'student':
            if request.method in ['GET', 'POST']:
                return True  # students can read and post answers
            return False  # no update/delete

        return False

    def has_object_permission(self, request, view, obj):
        # Object level permission: students can only access their own answers
        user = request.user
        if user.role in ['admin', 'teacher']:
            return True
        if user.role == 'student':
            return obj.user_quiz_id.user_id == user  # assuming user_quiz_id links to user
        return False

class IsAdminOrReadUpdate(BasePermission):
    """
    Custom permission to only allow admins to edit objects,
    while read-only access is granted to all authenticated users.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS_TASK:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        # For safe methods, always allow (even if user is not authenticated)
        if request.method in SAFE_METHODS_TASK:
            return True
        user = getattr(request, 'user', None)
        # For unsafe methods, only allow admin
        if not user or not getattr(user, 'is_authenticated', False):
            return False
        return getattr(user, 'role', None) == 'admin'
