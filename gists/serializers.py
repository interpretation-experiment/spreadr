from django.contrib.auth.models import User
from rest_framework import serializers

from gists.models import Sentence, Tree, Profile


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
    profiles = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    profile_urls = serializers.HyperlinkedRelatedField(
        source='profiles',
        view_name='profile-detail',
        many=True,
        read_only=True
    )
    untouched = serializers.SerializerMethodField()

    def get_untouched(self, obj):
        request = self.context['request']

        # Anonymous users have read nothing
        if not request.user.is_authenticated():
            return True

        # Users without a profile have read nothing
        if (not hasattr(request.user, 'profile')
                or request.user.profile is None):
            return True

        profile = request.user.profile
        return profile not in obj.profiles

    class Meta:
        model = Tree
        fields = (
            'id', 'url',
            'sentences', 'sentence_urls',
            'profiles', 'profile_urls',
            'untouched',
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
    children_urls = serializers.HyperlinkedRelatedField(
        source='children',
        view_name='sentence-detail',
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
            'children', 'children_urls',
            'text',
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
    tree_urls = serializers.HyperlinkedRelatedField(
        source='trees',
        view_name='tree-detail',
        many=True,
        read_only=True
    )
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

    class Meta:
        model = Profile
        fields = (
            'id', 'url',
            'created',
            'user', 'user_url', 'user_username',
            'trees', 'tree_urls',
            'sentences', 'sentence_urls',
            'suggestion_credit',
        )
        read_only_fields = (
            'user', 'suggestion_credit',
        )


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    profile_url = serializers.HyperlinkedRelatedField(
        source='profile',
        view_name='profile-detail',
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id', 'url', 'is_active',
            'email', 'username',
            'profile', 'profile_url',
        )
