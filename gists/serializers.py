from django.contrib.auth.models import User
from rest_framework import serializers

from gists.models import Sentence


class SentenceSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    author_url = serializers.HyperlinkedRelatedField(
        source='author',
        view_name='user-detail',
        read_only=True
    )
    author_username = serializers.ReadOnlyField(
        source='author.username'
    )
    parent_url = serializers.HyperlinkedRelatedField(
        source='parent',
        view_name='sentence-detail',
        read_only=True
    )
    children = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    children_urls = serializers.HyperlinkedRelatedField(
        source='children',
        view_name='sentence-detail',
        many=True,
        read_only=True
    )

    class Meta:
        model = Sentence
        fields = (
            'url', 'id',
            'created',
            'author', 'author_url', 'author_username',
            'parent', 'parent_url',
            'children', 'children_urls',
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
