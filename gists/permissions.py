from rest_framework import permissions
import logging
logger = logging.getLogger('django')


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff


class HasProfile(permissions.BasePermission):

    def has_permission(self, request, view):
        return (hasattr(request.user, 'profile')
                and request.user.profile is not None)


class HasQuestionnaire(HasProfile):

    def has_permission(self, request, view):
        # The HasProfile parent called here ensures request.user has a profile
        return (super(HasQuestionnaire, self).has_permission(request, view)
                and hasattr(request.user.profile, 'questionnaire')
                and request.user.profile.questionnaire is not None)


class ObjUserIsSelf(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class ObjProfileIsSelf(HasProfile):

    # The HasProfile parent ensures request.user has a profile

    def has_object_permission(self, request, view, obj):
        return obj.profile.user == request.user


class WantsCreate(permissions.BasePermission):

    def has_permission(self, request, view):
        logger.warn(view.action)
        return view.action == 'create'


class WantsUpdate(permissions.BasePermission):

    def has_permission(self, request, view):
        return view.action == 'update'


class WantsList(permissions.BasePermission):

    def has_permission(self, request, view):
        return view.action == 'list'


class WantsRetrieve(permissions.BasePermission):

    def has_permission(self, request, view):
        return view.action == 'retrieve'


class WantsDestroy(permissions.BasePermission):

    def has_permission(self, request, view):
        return view.action == 'destroy'


class IsAdminElseCreateUpdateRetrieveDestroyOnly(permissions.BasePermission):
    """
    Only allow admin users, else only creation, update, retrieve, or destroy.
    """

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        if view.action in ['retrieve', 'update', 'destroy']:
            return True
        return request.user.is_staff or (request.method == 'POST')


class IsAdminOrHasSelf(permissions.BasePermission):
    """
    Only allow admin users or owner.
    """

    def has_object_permission(self, request, view, obj):
        if request.method == 'OPTIONS':
            return True
        return request.user.is_staff or request.user == obj.user


class IsAdminOrSelfElseReadOnly(permissions.BasePermission):
    """
    Only allow admin users and self, else read only.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Ok if you're admin or if this is you
        return request.user.is_staff or request.user == obj


class IsAdminOrObjectHasSelfElseReadOnly(permissions.BasePermission):
    """
    Only allow admin users or if the object contains the authenticated user,
    else read only.
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


class IsAuthenticatedWithoutProfileElseReadUpdateOnly(
        permissions.BasePermission, ProfilePermissionMixin):
    """
    Only allow authenticated users that have no profile attached to create,
    the rest can read and update.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # You need to be authenticated to do anything else than safe stuff
        if not request.user.is_authenticated():
            return False

        # If you have no profile, you can create. If you have one,
        # you can only update it.
        return (self.is_authenticated_without_profile(request)
                or request.method in ['PUT', 'PATCH'])


class IsAuthenticatedWithProfile(permissions.BasePermission,
                                 ProfilePermissionMixin):
    """
    Only allow authenticated users that have a profile attached.
    """

    def has_permission(self, request, view):
        return self.is_authenticated_with_profile(request)


class IsAuthenticatedWithProfileElseReadOnly(permissions.BasePermission,
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
