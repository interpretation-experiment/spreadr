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


class ProfilePermissionMixin:
    """
    Check a user is authenticated with a profile.
    """

    def is_authenticated_with_profile(self, request):
        return (request.user.is_authenticated()
                and hasattr(request.user, 'profile')
                and request.user.profile is not None)

    def is_authenticated_without_profile(self, request):
        return (request.user.is_authenticated()
                and (not hasattr(request.user, 'profile')
                     or request.user.profile is None))


class IsAuthenticatedWithoutProfileOrReadOnly(permissions.BasePermission,
                                              ProfilePermissionMixin):
    """
    Only allow authenticated users that have no profile attached.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return self.is_authenticated_without_profile(request)


class IsAuthenticatedWithProfile(permissions.BasePermission,
                                 ProfilePermissionMixin):
    """
    Only allow authenticated users that have a profile attached.
    """

    def has_permission(self, request, view):
        return self.is_authenticated_with_profile(request)


class IsAuthenticatedWithProfileOrReadOnly(permissions.BasePermission,
                                           ProfilePermissionMixin):
    """
    Only allow authenticated users that have a profile attached,
    else read-only.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return self.is_authenticated_with_profile(request)


class HasSuggestionCreditOrIsStaffOrReadOnly(permissions.BasePermission,
                                             ProfilePermissionMixin):
    """
    Only allow staff or profiles with positive suggestion credit.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # We need authentication, and a profile
        if not self.is_authenticated_with_profile(request):
            return False

        # Staff can do what it wants
        if request.user.is_staff:
            return True

        # Normal users must have suggestion credit
        return request.user.profile.suggestion_credit > 0
