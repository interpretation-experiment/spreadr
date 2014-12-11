from gists.models import Sentence
from gists.serializers import SentenceSerializer
from rest_framework import mixins
from rest_framework import generics


class SentenceList(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   generics.GenericAPIView):
    """
    List all sentences, or create a new sentence.
    """
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SentenceDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    """
    Retrieve, update or delete a sentence.
    """
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
