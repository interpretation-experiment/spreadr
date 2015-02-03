from django.contrib.auth.models import User
from django.db.models import Count
from django.conf import settings
from rest_framework import viewsets, mixins, filters, generics
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated

from gists.filters import SampleFilterBackend, UnreadFilterBackend
from gists.models import Sentence, Tree, Profile
from gists.serializers import (SentenceSerializer, TreeSerializer,
                               ProfileSerializer, UserSerializer)
from gists.permissions import (IsAdminOrObjectHasSelfOrReadOnly,
                               IsAuthenticatedWithoutProfileOrReadOnly,
                               IsAuthenticatedWithProfile,
                               IsAuthenticatedWithProfileOrReadOnly)


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
    filter_backends = (filters.OrderingFilter,
                       filters.SearchFilter,
                       UnreadFilterBackend,
                       SampleFilterBackend,)
    ordering = ('-created',)
    ordering_fields = ('created',)
    search_fields = ('text',)

    @classmethod
    def obtain_free_tree(cls):
        trees = Tree.objects.annotate(n_sentences=Count('sentences'))
        free_trees = trees.filter(n_sentences=0)
        if free_trees.count() > 0:
            return free_trees.first()
        else:
            tree = Tree()
            tree.save()
            return tree

    def perform_create(self, serializer):
        parent = serializer.validated_data.get('parent')
        tree = self.obtain_free_tree() if parent is None else parent.tree
        serializer.save(profile=self.request.user.profile, tree=tree)


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
    #ordering = ('user__username',)
    #ordering_fields =
    #search_fields =

    @list_route(permission_classes=[IsAuthenticatedWithProfile])
    def me(self, request, format=None):
        serializer = ProfileSerializer(request.user.profile,
                                       context={'request': request})
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User list and detail, read-only.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    ordering = ('username',)
    ordering_fields = ('username',)
    search_fields = ('username',)

    @list_route(permission_classes=[IsAuthenticated])
    def me(self, request, format=None):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
