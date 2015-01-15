from django.contrib.auth.models import User
from rest_framework import serializers

from gists.models import Sentence


class SentenceSerializer(serializers.HyperlinkedModelSerializer):
    author_url = serializers.HyperlinkedRelatedField(
        source='author',
        view_name='user-detail',
        read_only=True
    )
    author_id = serializers.PrimaryKeyRelatedField(
        source='author',
        read_only=True
    )

    class Meta:
        model = Sentence
        fields = ('url', 'id', 'created', 'author_url', 'author_id', 'text',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    sentence_urls = serializers.HyperlinkedRelatedField(
        source='sentences',
        many=True,
        view_name='sentence-detail',
        read_only=True
    )
    sentence_ids = serializers.PrimaryKeyRelatedField(
        source='sentences',
        many=True,
        queryset=Sentence.objects.all(),
    )

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'sentence_urls', 'sentence_ids',)
