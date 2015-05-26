from django.contrib.auth.models import User
from django.db.models import Count
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import viewsets, mixins, generics, filters
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from allauth.account.models import EmailAddress

from gists.filters import TreeFilter
from gists.models import (Sentence, Tree, Profile, GistsConfiguration,
                          LANGUAGE_CHOICES, OTHER_LANGUAGE, DEFAULT_LANGUAGE)
from gists.serializers import (SentenceSerializer, TreeSerializer,
                               ProfileSerializer, UserSerializer,
                               PrivateUserSerializer, EmailAddressSerializer)
from gists.permissions import (IsAdminElseCreateUpdateRetrieveDestroyOnly,
                               IsAdminOrHasSelf,
                               IsAdminOrSelfElseReadOnly,
                               IsAdminOrObjectHasSelfElseReadOnly,
                               IsAuthenticatedWithoutProfileElseReadUpdateOnly,
                               IsAuthenticatedWithProfile,
                               IsAuthenticatedWithProfileElseReadOnly,)


def confirm_email(request, key=None):
    domain = get_current_site(request).domain
    url = 'http://{}/profile/emails/confirm?key={}'.format(domain, key)
    return redirect(url)


class APIRoot(generics.GenericAPIView):
    """
    API Root.
    """
    def get(self, request, format=None):
        return Response({
            'trees': reverse('tree-list', request=request, format=format),
            'sentences': reverse('sentence-list', request=request,
                                 format=format),
            'profiles': reverse('profile-list', request=request,
                                format=format),
            'users': reverse('user-list', request=request, format=format),
            'emails': reverse('email-list', request=request, format=format),
            'meta': reverse('meta', request=request, format=format),
        })


class Meta(generics.GenericAPIView):
    """
    Meta information about the server.
    """
    def get(self, request, format=None):
        config = GistsConfiguration.get_solo()
        return Response({
            'version': settings.VERSION,
            'supported_languages': map(lambda l: {'name': l[0], 'label': l[1]},
                                       LANGUAGE_CHOICES),
            'other_language': OTHER_LANGUAGE,
            'default_language': DEFAULT_LANGUAGE,
            'base_credit': config.base_credit,
            'target_branch_count': config.target_branch_count,
            'target_branch_depth': config.target_branch_depth,
            'experiment_work': config.experiment_work,
            'training_work': config.training_work,
            'tree_cost': config.tree_cost,
        })


class TreeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Tree list and detail, read only.
    """
    queryset = Tree.objects.all()
    serializer_class = TreeSerializer
    filter_class = TreeFilter
    filter_backends = (filters.DjangoFilterBackend,)


class SentenceViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
    Sentence list and detail, unauthenticated read, authenticated creation.
    """
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer
    permission_classes = (IsAuthenticatedWithProfileElseReadOnly,)
    ordering = ('-created',)

    @classmethod
    def obtain_free_tree(cls):
        trees = Tree.objects.annotate(sentences_count=Count('sentences'))
        return trees.filter(sentences_count=0).first() or Tree.objects.create()

    def perform_create(self, serializer):
        profile = self.request.user.profile

        parent = serializer.validated_data.get('parent')
        if parent is None:
            # We're creating a new tree, check we're staff
            # or have suggestion credit
            if not (profile.user.is_staff or profile.suggestion_credit > 0):
                raise PermissionDenied
            tree = self.obtain_free_tree()
            tree_as_root = tree
        else:
            tree = parent.tree
            tree_as_root = None

        serializer.save(profile=profile, tree=tree, tree_as_root=tree_as_root)


class ProfileViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """
    Profile list and detail, unauthenticated read, authenticated creation
    and modification.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticatedWithoutProfileElseReadUpdateOnly,
                          IsAdminOrObjectHasSelfElseReadOnly,)
    ordering = ('user__username',)

    @list_route(permission_classes=[IsAuthenticatedWithProfile])
    def me(self, request, format=None):
        serializer = ProfileSerializer(request.user.profile,
                                       context={'request': request})
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    User list and detail, unauthenticated read, authenticated and modification
    (everything if staff, only username if self).
    """
    queryset = User.objects.all()
    permission_classes = (IsAdminOrSelfElseReadOnly,)
    ordering = ('username',)

    @list_route(permission_classes=[IsAuthenticated])
    def me(self, request, format=None):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def perform_update(self, serializer):
        """Allow changing the username.

        'is_active' and 'is_staff' are blocked here, and 'email' is not a
        writable field on the serializer. so nothing but the username can be
        changed."""

        user = self.request.user
        obj = self.get_object()
        data = serializer.validated_data

        is_active_change = ('is_active' in data and
                            obj.is_active != data['is_active'])
        is_staff_change = ('is_staff' in data and
                           obj.is_staff != data['is_staff'])

        if ((is_staff_change or is_active_change) and not user.is_staff):
            raise PermissionDenied("Non-staff user cannot change "
                                   "'is_staff' or 'is_active'")
        serializer.save()

    def get_serializer_class(self):
        user = self.request.user

        # In list view, only staff gets to see everything
        if self.action == 'list':
            return PrivateUserSerializer if user.is_staff else UserSerializer

        # In detail view, staff and self see everything
        if self.action == 'retrieve':
            obj = self.get_object()
            if user.is_staff or user == obj:
                return PrivateUserSerializer
            else:
                return UserSerializer

        # Otherwise, default to public view
        return UserSerializer


class EmailAddressViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    Email adresses list and detail, authenticated (staff or self) read and
    destroy, authenticated (any) create.
    """
    queryset = EmailAddress.objects.all()
    serializer_class = EmailAddressSerializer
    permission_classes = (IsAuthenticated,
                          IsAdminElseCreateUpdateRetrieveDestroyOnly,
                          IsAdminOrHasSelf,)
    ordering = ('user__username',)

    @detail_route(methods=['post'])
    def verify(self, request, pk=None):
        email = get_object_or_404(self.queryset, pk=pk)
        email.send_confirmation(request)
        return Response({'status': "A verification email has been sent "
                         "to '{}', please follow the "
                         "instructions in it".format(email.email)})

    def perform_create(self, serializer):
        """Send a confirmation email to the new address."""
        serializer.save(user=self.request.user)
        if not serializer.instance.verified:
            serializer.instance.send_confirmation(self.request)

    def perform_update(self, serializer):
        """Send a confirmation email to the new address."""
        serializer.save()
        if not serializer.instance.verified:
            serializer.instance.send_confirmation(self.request)

    def perform_destroy(self, instance):
        """Prevent deleting a primary address if it's not the last one."""
        other_emails = instance.user.emailaddress_set.exclude(pk=instance.pk)
        if other_emails.count() > 0:
            if instance.primary:
                raise PermissionDenied("Can't delete a primary address if "
                                       "it's not the last one")
        else:
            instance.user.email = ""
            instance.user.save()
        instance.delete()
