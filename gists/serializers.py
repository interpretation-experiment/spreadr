from django.contrib.auth.models import User
from rest_framework import serializers

from gists.models import Sentence


class SentenceSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Sentence
        fields = ('id', 'created', 'author', 'text',)


class UserSerializer(serializers.ModelSerializer):
    sentences = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Sentence.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'sentences',)
