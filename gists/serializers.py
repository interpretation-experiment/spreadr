from django.contrib.auth.models import User
from rest_framework import serializers

from gists.models import Sentence, Tree


class TreeSerializer(serializers.ModelSerializer):
    sentences = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    sentence_urls = serializers.HyperlinkedRelatedField(
        source='sentences',
        view_name='sentence-detail',
        many=True,
        read_only=True
    )
    authors = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    author_urls = serializers.HyperlinkedRelatedField(
        source='authors',
        view_name='user-detail',
        many=True,
        read_only=True
    )

    class Meta:
        model = Tree
        fields = (
            'url', 'id',
            'sentences', 'sentence_urls',
            'authors', 'author_urls',
        )


class SentenceSerializer(serializers.ModelSerializer):
    tree = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    tree_url = serializers.HyperlinkedRelatedField(
        source='tree',
        view_name='tree-detail',
        read_only=True
    )
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
            'tree', 'tree_url',
            'author', 'author_url', 'author_username',
            'parent', 'parent_url',
            'children', 'children_urls',
            'text',
        )


class UserSerializer(serializers.ModelSerializer):
    #trees = serializers.PrimaryKeyRelatedField(
        #many=True,
        #read_only=True
    #)
    #tree_urls = serializers.HyperlinkedRelatedField(
        #source='trees',
        #view_name='tree-detail',
        #many=True,
        #read_only=True
    #)
    sentences = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    sentence_urls = serializers.HyperlinkedRelatedField(
        source='sentences',
        view_name='sentence-detail',
        many=True,
        read_only=True
    )

    def trees(self):
        return set([s.tree for s in self.sentences])

    class Meta:
        model = User
        fields = (
            'url', 'id',
            'username',
            #'trees', 'tree_urls',
            'sentences', 'sentence_urls',
            'password',
        )
        write_only_fields = (
            'password',
        )

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super(UserSerializer, self).update(instance, validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
            user.save()
        return user
