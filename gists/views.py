from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from gists.models import Sentence
from gists.serializers import SentenceSerializer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def sentence_list(request):
    """
    List all sentences, or create a new sentence.
    """
    if request.method == 'GET':
        sentences = Sentence.objects.all()
        serializer = SentenceSerializer(sentences, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = SentenceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)


@csrf_exempt
def sentence_detail(request, pk):
    """
    Retrieve, update or delete a sentence.
    """
    try:
        sentence = Sentence.objects.get(pk=pk)
    except Sentence.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = SentenceSerializer(sentence)
        return JSONResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = SentenceSerializer(sentence, data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data)
        return JSONResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        sentence.delete()
        return HttpResponse(status=204)
