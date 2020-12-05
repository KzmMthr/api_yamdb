from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners admins or moders edit it.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_admin or request.user.is_superuser
        return False


class IsOwnerOrModerOrAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Custom permission to only allow owners or admins or moders edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return obj.author == request.user or request.user.is_moderator \
                   or request.user.is_admin or request.user.is_superuser
        return False


class IsAdminNotModerator(permissions.BasePermission):
    """
    Custom permission to give access only to admin but not moderators.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_admin
        return False

