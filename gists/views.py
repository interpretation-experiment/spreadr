from gists.models import Sentence
from gists.serializers import SentenceSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class SentenceList(APIView):
    """
    List all sentences, or create a new sentence.
    """
    def get(self, request, format=None):
        sentences = Sentence.objects.all()
        serializer = SentenceSerializer(sentences, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SentenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SentenceDetail(APIView):
    """
    Retrieve, update or delete a sentence.
    """
    def get_object(self, pk):
        try:
            return Sentence.objects.get(pk=pk)
        except Sentence.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        sentence = self.get_object(pk)
        serializer = SentenceSerializer(sentence)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        sentence = self.get_object(pk)
        serializer = SentenceSerializer(sentence, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        sentence = self.get_object(pk)
        sentence.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
