from django.contrib.auth.models import User
from rest_framework import serializers

from gists.models import (Sentence, Tree, Profile, LANGUAGE_CHOICES,
                          OTHER_LANGUAGE, DEFAULT_LANGUAGE)


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
    children_count = serializers.ReadOnlyField(
        source='children.count'
    )

    class Meta:
        model = Sentence
        fields = (
            'id', 'url',
            'created',
            'tree', 'tree_url',
            'profile', 'profile_url', 'profile_username',
            'parent', 'parent_url',
            'children', 'children_count',
            'text', 'language',
        )


class TreeSerializer(serializers.ModelSerializer):
    root = SentenceSerializer()
    sentences = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    profiles = serializers.PrimaryKeyRelatedField(
        source='distinct_profiles',
        many=True,
        read_only=True
    )
    network_edges = serializers.SerializerMethodField()

    def get_network_edges(self, obj):
        edges = obj.sentences.values('pk', 'children')
        return [{'source': e['pk'], 'target': e['children']} for e in edges
                if e['pk'] is not None and e['children'] is not None]

    class Meta:
        model = Tree
        fields = (
            'id', 'url',
            'root',
            'sentences',
            'profiles',
            'network_edges',
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
        source='distinct_trees',
        many=True,
        read_only=True
    )
    sentences = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    mothertongue = serializers.ChoiceField(choices=LANGUAGE_CHOICES)
    untouched_trees_count = serializers.SerializerMethodField()
    untouched_defaultlanguage_trees_count = serializers.SerializerMethodField()
    available_mothertongue_otheraware_trees_count = \
        serializers.SerializerMethodField()

    def get_untouched_trees_count(self, obj):
        """Count all trees the profile has not participated in."""
        return Tree.objects\
            .exclude(pk__in=obj.trees.values_list('pk', flat=True))\
            .count()

    def get_untouched_defaultlanguage_trees_count(self, obj):
        """Count all trees in DEFAULT_LANGUAGE the profile has not
        participated in."""
        return Tree.objects\
            .filter(root__language=DEFAULT_LANGUAGE)\
            .exclude(pk__in=obj.trees.values_list('pk', flat=True))\
            .count()

    def get_available_mothertongue_otheraware_trees_count(self, obj):
        """Other- and mothertongue-aware count of available trees.

        If the profile's mothertongue is not OTHER_LANGUAGE, count trees in the
        profile's language in which neither the profile nor profiles in
        OTHER_LANGUAGE have participated.

        (In this count, trees created by a profile in OTHER_LANGUAGE but with a
        single sentence, i.e. only root, will never appear. (As well as bigger
        trees where a profile in OTHER_LANGUAGE has participated.))

        If the profile's mothertongue is OTHER_LANGUAGE, count trees in
        DEFAULT_LANGUAGE in which at least one profile in OTHER_LANGUAGE has
        participated.

        (In this count, trees created by a profile in OTHER_LANGUAGE, in a
        language other than DEFAULT_LANGUAGE, will never appear.)
        """

        language = obj.mothertongue
        if language == OTHER_LANGUAGE:
            # Count trees in DEFAULT_LANGUAGE,
            # touched by profiles in OTHER_LANGUAGE
            return Tree.objects\
                .filter(root__language=DEFAULT_LANGUAGE)\
                .filter(profiles__mothertongue=OTHER_LANGUAGE)\
                .exclude(pk__in=obj.trees.values_list('pk', flat=True))\
                .count()
        else:
            # Count trees in the profile's language,
            # untouched by profiles in OTHER_LANGUAGE
            return Tree.objects\
                .filter(root__language=language)\
                .exclude(profiles__mothertongue=OTHER_LANGUAGE)\
                .exclude(pk__in=obj.trees.values_list('pk', flat=True))\
                .count()

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
            'untouched_defaultlanguage_trees_count',
            'available_mothertongue_otheraware_trees_count',
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
