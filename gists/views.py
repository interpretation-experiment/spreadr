from django.contrib.auth.models import User
from rest_framework import permissions, viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from gists.models import Sentence
from gists.serializers import SentenceSerializer, UserSerializer
from gists.permissions import IsOwnerOrReadOnly


class SentenceViewSet(viewsets.ModelViewSet):
    """
    Sentence list and detail, unauthenticated read, authenticated read-write.
    """
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User list and detail, read-only.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @list_route(permission_classes=[IsAuthenticated])
    def me(self, request, format=None):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
