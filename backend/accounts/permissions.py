"""
Custom permission classes for role-based access control.
"""

from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    """
    Permission class that allows access only to users with student role.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'student'
        )


class IsInstructor(permissions.BasePermission):
    """
    Permission class that allows access only to users with instructor role.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'instructor'
        )


class IsPharmacist(permissions.BasePermission):
    """
    Permission class that allows access only to users with pharmacist role.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'pharmacist'
        )


class IsAdmin(permissions.BasePermission):
    """
    Permission class that allows access only to users with admin role.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsStudentOrInstructor(permissions.BasePermission):
    """
    Permission class that allows access to users with student or instructor role.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['student', 'instructor']
        )


class IsInstructorOrAdmin(permissions.BasePermission):
    """
    Permission class that allows access to users with instructor or admin role.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['instructor', 'admin']
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class that allows access to object owner or admin.
    Requires the object to have a 'user' or 'owner' attribute.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.role == 'admin':
            return True
        
        # Check if object has user or owner attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows read-only access to all authenticated users,
    but write access only to instructors and admins.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Read permissions for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for instructors and admins
        return request.user.role in ['instructor', 'admin']


def require_role(*roles):
    """
    Decorator for view-level access control based on user roles.
    
    Usage:
        @require_role('instructor', 'admin')
        def my_view(request):
            ...
    
    Args:
        *roles: Variable number of role strings ('student', 'instructor', 'admin')
    
    Returns:
        Decorator function that checks if user has one of the specified roles
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                from rest_framework.exceptions import NotAuthenticated
                raise NotAuthenticated("Authentication required")
            
            if request.user.role not in roles:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    f"This action requires one of the following roles: {', '.join(roles)}"
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator
