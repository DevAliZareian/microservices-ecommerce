"""
Common permission classes used across services.
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read access to anyone, but only admin users can modify.
    Works with JWT tokens that have 'is_staff' claim.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and (request.user.is_staff or request.user.is_superuser)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission: only allow owners of an object to edit it.
    Assumes the model has a 'user_id' or 'user' field.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check for user_id field (used when referencing users from other services)
        if hasattr(obj, 'user_id'):
            return obj.user_id == request.user.id

        # Check for user foreign key
        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False


class IsServiceAccount(permissions.BasePermission):
    """
    Permission for internal service-to-service communication.
    Expects a custom header or a specific service token.
    """
    def has_permission(self, request, view):
        service_key = request.headers.get('X-Service-Key')
        return service_key == getattr(view, 'service_key', None)