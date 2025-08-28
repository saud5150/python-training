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
    
# In users/permissions.py or quiz/permissions.py

from rest_framework import permissions

class IsAdminOrReadOnlyAuthenticated(permissions.BasePermission):
    """
    Custom permission to only allow admin users to create/update/delete.
    All authenticated users can read (GET).
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Allow GET (read) for all authenticated users
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        
        # Only admin can POST, PUT, PATCH, DELETE
        return hasattr(request.user, 'role') and request.user.role == 'admin'
    
    def has_object_permission(self, request, view, obj):
        # Same logic for object-level permissions
        if not request.user.is_authenticated:
            return False
        
        # Allow read for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only admin can modify
        return hasattr(request.user, 'role') and request.user.role == 'admin'