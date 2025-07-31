from rest_framework.permissions import BasePermission, SAFE_METHODS

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
