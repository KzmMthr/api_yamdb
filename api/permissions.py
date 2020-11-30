from rest_framework import permissions

from users.models import CustomUser


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners admins or moders edit it.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        is_admin = getattr(request.user, 'is_admin', False)
        return is_admin or request.user.is_superuser


class IsOwnerOrModerOrAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Custom permission to only allow owners or admins or moders edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff or request.user.is_superuser \
               or obj.author == request.user or request.user.role == CustomUser.Roles.MODERATOR


class IsAdminNotModerator(permissions.BasePermission):
    """
    Custom permission to give access only to admin but not moderators.
    """
    def has_permission(self, request, view):
        return request.user.is_staff and request.user.is_admin
