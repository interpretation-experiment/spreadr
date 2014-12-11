from rest_framework import serializers
from gists.models import Sentence


class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = ('id', 'created', 'text',)
