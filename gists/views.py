from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.db.models import Count
from rest_framework import permissions, viewsets, mixins, filters
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from gists.filters import SampleFilterBackend, UnreadFilterBackend
from gists.models import Sentence, Tree
from gists.serializers import (SentenceSerializer, UserSerializer,
                               TreeSerializer)
from gists.permissions import IsAdminOrSelfOrReadOnly


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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
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
        serializer.save(author=self.request.user, tree=tree)


class UserViewSet(viewsets.ModelViewSet):
    """
    User list and detail, unauthenticated registration,
    authenticated modification.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrSelfOrReadOnly,)
    ordering = ('username',)
    ordering_fields = ('username',)
    search_fields = ('username',)

    @list_route(permission_classes=[IsAuthenticated])
    def me(self, request, format=None):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def perform_update(self, serializer):
        super(UserViewSet, self).perform_update(serializer)
        update_session_auth_hash(self.request, serializer.instance)
