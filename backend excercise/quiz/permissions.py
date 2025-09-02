from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsTeacherOrReadOnlyForStudents(BasePermission):
    """
    Custom permission:
    - Teachers have full access (POST, PUT, PATCH, DELETE).
    - Students have read-only access (GET, HEAD, OPTIONS).
    - Others are denied.
    """

    def has_permission(self, request, view):
        claims = request.auth  # Use JWT claims, not request.user
        if not claims:
            return False

        role = claims.get('role')
        if role in ['admin', 'teacher']:
            return True  # full CRUD

        if role == 'student':
            if request.method in SAFE_METHODS:
                return True  # students can read
            return False

        return False
    
# In users/permissions.py or quiz/permissions.py

class IsAdminOrReadOnlyAuthenticated(BasePermission):
    def has_permission(self, request, view):
        claims = request.auth
        if not claims:
            return False
        # Allow read for all authenticated users
        if request.method in SAFE_METHODS:
            return True
        # Only admin can write
        return claims.get('role') == 'admin'