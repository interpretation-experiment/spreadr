from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from rest_framework import serializers
from allauth.account.models import EmailAddress

from gists.models import (Sentence, Tree, Profile, LANGUAGE_CHOICES,
                          OTHER_LANGUAGE, DEFAULT_LANGUAGE, BUCKET_CHOICES)


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
            'text', 'language', 'bucket',
        )


class TreeSerializer(serializers.ModelSerializer):
    root = SentenceSerializer()
    sentences = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    sentences_count = serializers.ReadOnlyField(
        source='sentences.count'
    )
    profiles = serializers.PrimaryKeyRelatedField(
        source='distinct_profiles',
        many=True,
        read_only=True
    )
    branches_count = serializers.ReadOnlyField(
        source='root.children.count'
    )

    class Meta:
        model = Tree
        fields = (
            'id', 'url',
            'root',
            'sentences', 'sentences_count',
            'profiles',
            'network_edges',
            'branches_count', 'shortest_branch_depth',
        )
        read_only_fields = (
            'network_edges',
            'shortest_branch_depth',
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
    trees_count = serializers.ReadOnlyField(
        source='distinct_trees.count'
    )
    sentences = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    sentences_count = serializers.ReadOnlyField(
        source='sentences.count'
    )
    mothertongue = serializers.ChoiceField(choices=LANGUAGE_CHOICES)
    available_trees_counts = serializers.SerializerMethodField()

    def get_available_trees_counts(self, obj):
        """Other- and mothertongue-aware count of available trees, per bucket.

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

        Counts are returned ber bucket.
        """

        language = obj.mothertongue
        if language == OTHER_LANGUAGE:
            # Count trees in DEFAULT_LANGUAGE,
            # touched by profiles in OTHER_LANGUAGE
            qs = Tree.objects\
                .filter(root__language=DEFAULT_LANGUAGE)\
                .filter(profiles__mothertongue=OTHER_LANGUAGE)\
                .exclude(pk__in=obj.trees.values_list('pk', flat=True))
        else:
            # Count trees in the profile's language,
            # untouched by profiles in OTHER_LANGUAGE
            qs = Tree.objects\
                .filter(root__language=language)\
                .exclude(profiles__mothertongue=OTHER_LANGUAGE)\
                .exclude(pk__in=obj.trees.values_list('pk', flat=True))

        return dict((bucket[0], qs.filter(root__bucket=bucket[0]).count())
                    for bucket in BUCKET_CHOICES)

    class Meta:
        model = Profile
        fields = (
            'id', 'url',
            'created',
            'trained_reformulations',
            'user', 'user_url', 'user_username',
            'trees', 'trees_count',
            'sentences', 'sentences_count',
            'reformulations_count',
            'suggestion_credit',
            'next_credit_in',
            'mothertongue',
            'available_trees_counts',
            'introduced_exp_home', 'introduced_exp_play',
            'introduced_play_home', 'introduced_play_play',
        )
        read_only_fields = (
            'user', 'suggestion_credit',
        )


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        is_active_change = ('is_active' in validated_data and
                            instance.is_active != validated_data['is_active'])
        is_staff_change = ('is_staff' in validated_data and
                           instance.is_staff != validated_data['is_staff'])
        is_email_change = ('email' in validated_data and
                           instance.email != validated_data['email'])
        if ((is_staff_change or is_active_change or is_email_change)
                and not user.is_staff):
            raise PermissionDenied("Non-staff user cannot change "
                                   "'is_staff', 'is_active', or 'email'")
        return super(UserSerializer, self).update(instance, validated_data)

    class Meta:
        model = User
        fields = (
            'id', 'url', 'is_active', 'is_staff',
            'username',
            'profile',
        )


class PrivateUserSerializer(UserSerializer):
    emails = serializers.PrimaryKeyRelatedField(
        source='emailaddress_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id', 'url', 'is_active', 'is_staff',
            'username',
            'profile',
            'emails',
        )


class EmailAddressSerializer(serializers.ModelSerializer):
    user_url = serializers.HyperlinkedRelatedField(
        source='user',
        view_name='user-detail',
        read_only=True
    )

    class Meta:
        model = EmailAddress
        fields = (
            'id', 'url',
            'user', 'user_url',
            'email',
            'verified', 'primary',
        )
        read_only_fields = (
            'user', 'user_url',
            'email',
            'verified', 'primary',
        )
