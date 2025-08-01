from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsTeacherOrReadOnlyForStudents(BasePermission):
    """
    Custom permission:
    - Teachers have full access (POST, PUT, PATCH, DELETE).
    - Students have read-only access (GET, HEAD, OPTIONS).
    - Others are denied.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role in ['admin', 'teacher']:
            return True  # full CRUD

        if user.role == 'student':
            if request.method in ['GET']:
                return True  # students can read
            return False
        
        return False
    