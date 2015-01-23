from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from rest_framework import permissions, viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from gists.models import Sentence
from gists.serializers import SentenceSerializer, UserSerializer
from gists.permissions import IsOwnerOrReadOnly, IsAdminOrSelfOrReadOnly


class SentenceViewSet(viewsets.ModelViewSet):
    """
    Sentence list and detail, unauthenticated read, authenticated read-write.
    """
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    ordering = ('-created',)
    ordering_fields = ('created',)
    search_fields = ('text',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    """
    User list and detail, unauthenticated registration, authenticated modification.
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
