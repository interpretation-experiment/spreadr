from django.contrib.auth.models import User
from rest_framework import permissions, viewsets

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
