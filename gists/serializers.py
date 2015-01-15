from django.contrib.auth.models import User
from rest_framework import serializers

from gists.models import Sentence


class SentenceSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(
        source='author.username'
    )
    author_url = serializers.HyperlinkedRelatedField(
        source='author',
        view_name='user-detail',
        read_only=True
    )

    class Meta:
        model = Sentence
        fields = (
            'url', 'id',
            'created',
            'author', 'author_url',
            'text',
        )


class UserSerializer(serializers.ModelSerializer):
    sentences = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Sentence.objects.all()
    )
    sentence_urls = serializers.HyperlinkedRelatedField(
        source='sentences',
        view_name='sentence-detail',
        many=True,
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'url', 'id',
            'username',
            'sentences', 'sentence_urls',
        )
