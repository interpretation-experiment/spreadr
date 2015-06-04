from django.http.response import Http404
from rest_framework import permissions


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


class HasReadingSpan(HasProfile):

    def has_permission(self, request, view):
        # The HasProfile parent called here ensures request.user has a profile
        return (super(HasReadingSpan, self).has_permission(request, view)
                and hasattr(request.user.profile, 'reading_span')
                and request.user.profile.reading_span is not None)


class ObjIsSelf(permissions.BasePermission):

    def has_permission(self, request, view):
        obj = view.get_object()
        return obj == request.user


class ObjUserIsSelf(permissions.BasePermission):

    def has_permission(self, request, view):
        try:
            obj = view.get_object()
            return obj.user == request.user
        except Http404:
            return False


class ObjProfileIsSelf(HasProfile):

    # The HasProfile parent ensures request.user has a profile

    def has_permission(self, request, view):
        try:
            obj = view.get_object()
            return obj.profile.user == request.user
        except Http404:
            return False


class WantsSafe(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class WantsPost(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method == 'POST'


class WantsCreate(permissions.BasePermission):

    def has_permission(self, request, view):
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
