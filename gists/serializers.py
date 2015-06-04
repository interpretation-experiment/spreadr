from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from rest_framework import serializers
from allauth.account.models import EmailAddress

from gists.models import (Sentence, Tree, Profile, Questionnaire,
                          ReadingSpan,
                          LANGUAGE_CHOICES, OTHER_LANGUAGE,
                          DEFAULT_LANGUAGE, BUCKET_CHOICES)


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
            'time_proportion', 'time_used', 'time_allotted',
        )
        read_only_fields = (
            'time_used',
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
    questionnaire = serializers.PrimaryKeyRelatedField(read_only=True)
    questionnaire_url = serializers.HyperlinkedRelatedField(
        source='questionnaire',
        view_name='questionnaire-detail',
        read_only=True
    )
    questionnaire_done = serializers.SerializerMethodField()
    reading_span = serializers.PrimaryKeyRelatedField(read_only=True)
    reading_span_url = serializers.HyperlinkedRelatedField(
        source='reading_span',
        view_name='reading-span-detail',
        read_only=True
    )
    reading_span_done = serializers.SerializerMethodField()
    available_trees_counts = serializers.SerializerMethodField()

    def get_questionnaire_done(self, obj):
        return (hasattr(obj, 'questionnaire') and
                obj.questionnaire is not None)

    def get_reading_span_done(self, obj):
        return (hasattr(obj, 'reading_span') and
                obj.reading_span is not None)

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
            'id', 'url', 'created',
            'user', 'user_url', 'user_username',

            'trees', 'trees_count',
            'sentences', 'sentences_count',
            'reformulations_count',

            'suggestion_credit', 'next_credit_in',
            'available_trees_counts',

            'mothertongue',
            'trained_reformulations',

            'questionnaire', 'questionnaire_url',
            'questionnaire_done',

            'reading_span', 'reading_span_url',
            'reading_span_done',

            'introduced_exp_home', 'introduced_exp_play',
            'introduced_play_home', 'introduced_play_play',
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

    def validate(self, data):
        has_isco_default = (data.get('isco_major', '')[:1] == '-' or
                            data.get('isco_submajor', '')[:1] == '-' or
                            data.get('isco_minor', '')[:1] == '-')
        if has_isco_default and len(data.get('isco_freetext', '')) < 3:
            raise serializers.ValidationError(
                "Enter at least three characters in your activity detail "
                "if you don't describe it by categories")
        return data

    class Meta:
        model = Questionnaire
        fields = (
            'id', 'url', 'created',
            'profile', 'profile_url',
            'age', 'gender',
            'naive', 'naive_detail',
            'isco_major', 'isco_submajor', 'isco_minor',
            'isco_freetext',
        )
        read_only_fields = (
            'created',
            'profile',
        )


class ReadingSpanSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='reading-span-detail')
    profile_url = serializers.HyperlinkedRelatedField(
        source='profile',
        view_name='profile-detail',
        read_only=True
    )

    def validate(self, data):
        span = data['span']
        words_count = data['words_count']
        if span > words_count:
            raise serializers.ValidationError((
                "Reading-span ({}) can't be more than the number of "
                "words it was tested on ({})").format(span, words_count))
        return data

    class Meta:
        model = ReadingSpan
        fields = (
            'id', 'url', 'created',
            'profile', 'profile_url',
            'words_count', 'span',
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
