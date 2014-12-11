from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from gists.models import Sentence
from gists.serializers import SentenceSerializer


@api_view(['GET', 'POST'])
def sentence_list(request, format=None):
    """
    List all sentences, or create a new sentence.
    """
    if request.method == 'GET':
        sentences = Sentence.objects.all()
        serializer = SentenceSerializer(sentences, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SentenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def sentence_detail(request, pk, format=None):
    """
    Retrieve, update or delete a sentence.
    """
    try:
        sentence = Sentence.objects.get(pk=pk)
    except Sentence.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SentenceSerializer(sentence)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SentenceSerializer(sentence, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        sentence.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
