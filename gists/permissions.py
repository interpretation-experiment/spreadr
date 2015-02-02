from rest_framework import permissions


class IsAdminOrObjectHasSelfOrReadOnly(permissions.BasePermission):
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


class IsAuthenticatedWithoutProfileOrReadOnly(permissions.BasePermission):
    """
    Only allow authenticated users that have no profile attached.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return (request.user.is_authenticated()
                and (not hasattr(request.user, 'profile')
                     or request.user.profile is None))


class IsAuthenticatedWithProfile(permissions.BasePermission):
    """
    Only allow authenticated users that have a profile attached.
    """

    def has_permission(self, request, view):
        return (request.user.is_authenticated()
                and hasattr(request.user, 'profile')
                and request.user.profile is not None)


class IsAuthenticatedWithProfileOrReadOnly(permissions.BasePermission):
    """
    Only allow authenticated users that have a profile attached,
    else read-only.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return (request.user.is_authenticated()
                and hasattr(request.user, 'profile')
                and request.user.profile is not None)
