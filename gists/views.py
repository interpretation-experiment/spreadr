from django.contrib.auth.models import User
from django.db.models import Count
from django.core.exceptions import PermissionDenied
from django.conf import settings
from rest_framework import viewsets, mixins, generics, filters
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated

from gists.filters import SampleFilterBackend, UntouchedFilterBackend, TreeFilter
from gists.models import Sentence, Tree, Profile
from gists.serializers import (SentenceSerializer, TreeSerializer,
                               ProfileSerializer, UserSerializer)
from gists.permissions import (IsAdminOrReadOnly,
                               IsAdminOrObjectHasSelfOrReadOnly,
                               IsAuthenticatedWithoutProfileOrReadOnly,
                               IsAuthenticatedWithProfile,
                               IsAuthenticatedWithProfileOrReadOnly,)


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
            'version': settings.VERSION,
        })


class TreeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Tree list and detail, read only.
    """
    queryset = Tree.objects.all()
    serializer_class = TreeSerializer
    filter_class = TreeFilter
    filter_backends = (filters.DjangoFilterBackend,
                       UntouchedFilterBackend,
                       SampleFilterBackend,)


class SentenceViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
    Sentence list and detail, unauthenticated read, authenticated creation.
    """
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer
    permission_classes = (IsAuthenticatedWithProfileOrReadOnly,)
    ordering = ('-created',)

    @classmethod
    def obtain_free_tree(cls):
        trees = Tree.objects.annotate(n_sentences=Count('sentences'))
        return trees.filter(n_sentences=0).first() or Tree.objects.create()

    def perform_create(self, serializer):
        profile = self.request.user.profile

        parent = serializer.validated_data.get('parent')
        if parent is None:
            # We're creating a new tree, check we're staff
            # or have suggestion credit
            if not (profile.user.is_staff or profile.suggestion_credit > 0):
                raise PermissionDenied
            tree = self.obtain_free_tree()
        else:
            tree = parent.tree

        serializer.save(profile=profile, tree=tree)


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
    permission_classes = (IsAuthenticatedWithoutProfileOrReadOnly,
                          IsAdminOrObjectHasSelfOrReadOnly,)
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
    User list and detail, read-only.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrReadOnly,)
    ordering = ('username',)

    @list_route(permission_classes=[IsAuthenticated])
    def me(self, request, format=None):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
