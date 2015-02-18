from django.contrib.auth.models import User
from rest_framework import serializers

from gists.models import Sentence, Tree, Profile, LANGUAGE_CHOICES


class SentenceSerializer(serializers.ModelSerializer):
    tree = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    tree_url = serializers.HyperlinkedRelatedField(
        source='tree',
        view_name='tree-detail',
        read_only=True
    )
    profile = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    profile_url = serializers.HyperlinkedRelatedField(
        source='profile',
        view_name='profile-detail',
        read_only=True
    )
    profile_username = serializers.ReadOnlyField(
        source='profile.user.username'
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

    class Meta:
        model = Sentence
        fields = (
            'id', 'url',
            'created',
            'tree', 'tree_url',
            'profile', 'profile_url', 'profile_username',
            'parent', 'parent_url',
            'children',
            'text', 'language',
        )


class TreeSerializer(serializers.ModelSerializer):
    root = SentenceSerializer()
    sentences = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Tree
        fields = (
            'id', 'url',
            'root',
            'sentences',
            'profiles',
        )


class ProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(
        source='user.username'
    )
    user_url = serializers.HyperlinkedRelatedField(
        source='user',
        view_name='user-detail',
        read_only=True
    )
    trees = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    sentences = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    mothertongue = serializers.ChoiceField(choices=LANGUAGE_CHOICES)
    untouched_trees_count = serializers.SerializerMethodField()

    def get_untouched_trees_count(self, obj):
        return Tree.objects.count() - obj.trees.count()

    class Meta:
        model = Profile
        fields = (
            'id', 'url',
            'created',
            'user', 'user_url', 'user_username',
            'trees',
            'sentences',
            'suggestion_credit',
            'mothertongue',
            'untouched_trees_count',
        )
        read_only_fields = (
            'user', 'suggestion_credit',
        )


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = (
            'id', 'url', 'is_active', 'is_staff',
            'email', 'username',
            'profile',
        )
