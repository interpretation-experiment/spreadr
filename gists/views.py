from gists.models import Sentence
from gists.serializers import SentenceSerializer
from rest_framework import generics


class SentenceList(generics.ListCreateAPIView):
    """
    List all sentences, or create a new sentence.
    """
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer


class SentenceDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a sentence.
    """
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer
