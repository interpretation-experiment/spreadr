from django.contrib.auth.models import User
from rest_framework import generics, permissions

from gists.models import Sentence
from gists.serializers import SentenceSerializer, UserSerializer
from gists.permissions import IsOwnerOrReadOnly


class SentenceList(generics.ListCreateAPIView):
    """
    List all sentences, or create a new sentence.
    """
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SentenceDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a sentence.
    """
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)


class UserList(generics.ListAPIView):
    """
    List all users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    """
    Retrieve a user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
