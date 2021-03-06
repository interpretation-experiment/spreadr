from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from rest_framework import serializers
from allauth.account.models import EmailAddress

from gists.models import (Sentence, Tree, Profile, Questionnaire,
                          WordSpan, Comment,
                          LANGUAGE_CHOICES, OTHER_LANGUAGE,
                          DEFAULT_LANGUAGE)


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
            'read_time_proportion', 'read_time_used', 'read_time_allotted',
            'write_time_proportion', 'write_time_used', 'write_time_allotted',
        )
        read_only_fields = (
            'read_time_used',
            'write_time_used',
        )


class TreeSerializer(serializers.ModelSerializer):
    root = SentenceSerializer()
    profile_lock = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    profile_lock_url = serializers.HyperlinkedRelatedField(
        source='profile_lock',
        view_name='profile-detail',
        read_only=True
    )
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
            'created',
            'root',
            'profile_lock', 'profile_lock_url',
            'profile_lock_heartbeat',
            'sentences', 'sentences_count',
            'profiles',
            'network_edges',
            'branches_count', 'shortest_branch_depth',
        )
        read_only_fields = (
            'profile_lock_heartbeat',
            'network_edges',
            'shortest_branch_depth',
        )


class ProfileSerializer(serializers.ModelSerializer):
    user_url = serializers.HyperlinkedRelatedField(
        source='user',
        view_name='user-detail',
        read_only=True
    )
    user_username = serializers.ReadOnlyField(
        source='user.username'
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
    tree_locks = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    sentences_counts = serializers.SerializerMethodField()
    reformulations_counts = serializers.SerializerMethodField()
    trees_counts = serializers.SerializerMethodField()
    available_trees_counts = serializers.SerializerMethodField()

    mothertongue = serializers.ChoiceField(choices=LANGUAGE_CHOICES)

    questionnaire = serializers.PrimaryKeyRelatedField(read_only=True)
    questionnaire_url = serializers.HyperlinkedRelatedField(
        source='questionnaire',
        view_name='questionnaire-detail',
        read_only=True
    )
    questionnaire_done = serializers.SerializerMethodField()

    word_span = serializers.PrimaryKeyRelatedField(read_only=True)
    word_span_url = serializers.HyperlinkedRelatedField(
        source='word_span',
        view_name='word-span-detail',
        read_only=True
    )
    word_span_done = serializers.SerializerMethodField()

    comments = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )
    comments_count = serializers.ReadOnlyField(
        source='comments.count'
    )

    def get_questionnaire_done(self, obj):
        return (hasattr(obj, 'questionnaire') and
                obj.questionnaire is not None)

    def get_word_span_done(self, obj):
        return (hasattr(obj, 'word_span') and
                obj.word_span is not None)

    def get_sentences_counts(self, obj):
        return Sentence.bucket_counts(obj.sentences)

    def get_reformulations_counts(self, obj):
        return Sentence.bucket_counts(obj.sentences.exclude(parent=None))

    def get_trees_counts(self, obj):
        return Tree.bucket_counts(obj.distinct_trees)

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

        return Tree.bucket_counts(qs)

    class Meta:
        model = Profile
        fields = (
            'id', 'url', 'created',
            'user', 'user_url', 'user_username',

            'trees', 'sentences', 'tree_locks',

            'sentences_counts', 'reformulations_counts',
            'trees_counts', 'available_trees_counts',

            'suggestion_credit', 'next_credit_in',

            'mothertongue',
            'trained_reformulations',

            'questionnaire', 'questionnaire_url',
            'questionnaire_done',

            'word_span', 'word_span_url', 'word_span_done',

            'comments', 'comments_count',

            'introduced_exp_home', 'introduced_exp_play',
            'introduced_play_home', 'introduced_play_play',

            'prolific_id',
        )
        read_only_fields = (
            'created',
            'user',
            'suggestion_credit',
        )


class QuestionnaireSerializer(serializers.ModelSerializer):
    profile_url = serializers.HyperlinkedRelatedField(
        source='profile',
        view_name='profile-detail',
        read_only=True
    )

    class Meta:
        model = Questionnaire
        fields = (
            'id', 'url', 'created',
            'profile', 'profile_url',
            'age', 'gender',
            'informed', 'informed_how', 'informed_what',
            'education_level', 'education_freetext',
            'job_type', 'job_freetext',
        )
        read_only_fields = (
            'created',
            'profile',
        )


class WordSpanSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='word-span-detail')
    profile_url = serializers.HyperlinkedRelatedField(
        source='profile',
        view_name='profile-detail',
        read_only=True
    )

    class Meta:
        model = WordSpan
        fields = (
            'id', 'url', 'created',
            'profile', 'profile_url',
            'span', 'score',
        )
        read_only_fields = (
            'created',
            'profile',
        )


class CommentSerializer(serializers.ModelSerializer):
    profile_url = serializers.HyperlinkedRelatedField(
        source='profile',
        view_name='profile-detail',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = (
            'id', 'url', 'created',
            'profile', 'profile_url',
            'email', 'meta', 'text',
        )
        read_only_fields = (
            'created',
            'profile',
        )


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'url', 'is_active', 'is_staff',
            'username',
            'profile',
        )


class EmailAddressSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='email-detail')
    user_url = serializers.HyperlinkedRelatedField(
        source='user',
        view_name='user-detail',
        read_only=True
    )

    def update(self, instance, validated_data):
        """Prevent setting 'primary' to false, and invalidate 'verified'
        if the address changes."""

        if 'primary' in validated_data:
            iprimary = instance.primary
            vprimary = validated_data['primary']
            if iprimary != vprimary:
                # 'primary' is being changed, but we only allow False -> True
                if iprimary and not vprimary:
                    raise PermissionDenied("Can't set 'primary' to False, "
                                           "do it by setting another email "
                                           "address to primary")
                instance.set_as_primary()
                del validated_data['primary']

        if ('email' in validated_data and
                validated_data['email'] != instance.email):
            # 'email' is being changed, so invalidate the verification
            validated_data['verified'] = False

        return super(EmailAddressSerializer, self).update(instance,
                                                          validated_data)

    def create(self, validated_data, **kwargs):
        """Prevent setting 'primary' to true if there is already another
        primary address, otherwise force setting to primary."""

        user = self.context['request'].user

        if user.emailaddress_set.filter(primary=True).count() > 0:
            # User already has a primary address
            if validated_data.get('primary', False):
                # Can't set two (must be done in two steps: first create,
                # then set primary)
                raise PermissionDenied("User already has a primary address")
            return super(EmailAddressSerializer, self).create(
                validated_data, **kwargs)

        else:
            # User has no primary address, use this one
            instance = super(EmailAddressSerializer, self).create(
                validated_data, **kwargs)
            instance.set_as_primary()
            return instance

    class Meta:
        model = EmailAddress
        fields = (
            'id', 'url',
            'user', 'user_url',
            'email',
            'verified',
            'primary',
        )
        read_only_fields = (
            'user', 'user_url',
            'verified',
        )


class PrivateUserSerializer(UserSerializer):
    emails = EmailAddressSerializer(
        source='emailaddress_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id', 'url', 'is_active', 'is_staff',
            'username',
            'email',
            'profile',
            'emails',
        )
        read_only_fields = (
            'email',
        )
