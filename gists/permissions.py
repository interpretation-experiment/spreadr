from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the snippet.
        return obj.author == request.user


class IsAdminOrSelfOrReadOnly(permissions.BasePermission):
    """
    Only allow admin users or if the object is the authenticated user.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin users are allowed everything
        if request.user.is_staff:
            return True

        # Otherwise, only self is allowed
        return obj == request.user


class IsAdminOrUserSelfOrReadOnly(permissions.BasePermission):
    """
    Only allow admin users or if the object contains the authenticated user.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin users are allowed everything
        if request.user.is_staff:
            return True

        # Otherwise, only self is allowed
        return obj.user == request.user


class IsAuthenticatedProfile(permissions.BasePermission):
    """
    Only allow authenticated users that have a profile attached.
    """

    def has_permission(self, request, view):
        return (request.user.is_authenticated()
                and hasattr(request.user, 'profile')
                and request.user.profile is not None)


class IsAuthenticatedProfileOrReadOnly(permissions.BasePermission):
    """
    Only allow authenticated users that have a profile attached.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return (request.user.is_authenticated()
                and hasattr(request.user, 'profile')
                and request.user.profile is not None)
