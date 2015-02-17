from django.contrib.auth.models import User
from rest_framework import serializers

from gists.models import Sentence, Tree, Profile, LANGUAGE_CHOICES


class TreeSerializer(serializers.ModelSerializer):
    root_url = serializers.HyperlinkedRelatedField(
        source='root',
        view_name='sentence-detail',
        read_only=True
    )
    root_language = serializers.ReadOnlyField(
        source='root.language'
    )
    profile_url = serializers.HyperlinkedRelatedField(
        source='profile',
        view_name='profile-detail',
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
        return profile.pk not in obj.sentences.values_list('profile',
                                                           flat=True)

    class Meta:
        model = Tree
        fields = (
            'id', 'url',
            'root', 'root_url', 'root_language',
            'profile', 'profile_url',
            'sentences', 'sentence_urls',
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
            'text', 'language',
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
    created_trees = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    created_trees_urls = serializers.HyperlinkedRelatedField(
        source='created_trees',
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
    mothertongue = serializers.ChoiceField(choices=LANGUAGE_CHOICES)

    class Meta:
        model = Profile
        fields = (
            'id', 'url',
            'created',
            'user', 'user_url', 'user_username',
            'created_trees', 'created_trees_urls',
            'sentences', 'sentence_urls',
            'suggestion_credit',
            'mothertongue',
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
            'id', 'url', 'is_active', 'is_staff',
            'email', 'username',
            'profile', 'profile_url',
        )
