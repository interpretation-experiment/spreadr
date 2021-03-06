from datetime import timedelta
try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now

from django.contrib.auth.models import User
from django.db.models import Count, Max, F, Q
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import viewsets, mixins, filters, views
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated
from allauth.account.models import EmailAddress
from rest_condition import C
from numpy.random import choice

from gists.filters import TreeFilter
from gists.models import (Sentence, Tree, Profile, Questionnaire,
                          WordSpan, Comment, GistsConfiguration,
                          LANGUAGE_CHOICES, OTHER_LANGUAGE, DEFAULT_LANGUAGE,
                          GENDER_CHOICES, EDUCATION_LEVEL_CHOICES,
                          JOB_TYPE_CHOICES,)
from gists.serializers import (SentenceSerializer, TreeSerializer,
                               ProfileSerializer, QuestionnaireSerializer,
                               WordSpanSerializer, CommentSerializer,
                               UserSerializer, PrivateUserSerializer,
                               EmailAddressSerializer)
from gists.permissions import (IsAdmin, HasProfile, HasQuestionnaire,
                               HasWordSpan, ObjIsSelf, ObjUserIsSelf,
                               WantsSafe, WantsPost,
                               WantsCreate, WantsUpdate, WantsList,
                               WantsRetrieve, WantsDestroy,)


def remap_choices(choices):
    return map(lambda l: {'name': l[0], 'label': l[1]}, choices)


def is_user_authenticated_with_profile(user):
    return (user.is_authenticated() and
            hasattr(user, 'profile') and
            user.profile is not None)


def confirm_email(request, key=None):
    domain = get_current_site(request).domain
    url = 'http://{}/profile/emails/confirm?key={}'.format(domain, key)
    return redirect(url)


class APIRoot(views.APIView):
    """
    API Root.
    """
    def get(self, request, format=None):
        return Response({
            'trees': reverse('tree-list', request=request, format=format),
            'sentences': reverse('sentence-list', request=request,
                                 format=format),
            'profiles': reverse('profile-list', request=request,
                                format=format),
            'questionnaires': reverse('questionnaire-list', request=request,
                                      format=format),
            'word-spans': reverse('word-span-list', request=request,
                                  format=format),
            'comments': reverse('comment-list', request=request,
                                format=format),
            'users': reverse('user-list', request=request, format=format),
            'emails': reverse('email-list', request=request, format=format),
            'meta': reverse('meta', request=request, format=format),
            'stats': reverse('stats', request=request, format=format),
        })


class Meta(views.APIView):
    """
    Meta information about the server.
    """
    def get(self, request, format=None):
        config = GistsConfiguration.get_solo()
        return Response({
            # Tree shaping
            'target_branch_depth': config.target_branch_depth,
            'target_branch_count': config.target_branch_count,
            'branch_probability': config.branch_probability,

            # Read-write parameters
            'read_factor': config.read_factor,
            'write_factor': config.write_factor,
            'min_tokens': config.min_tokens,
            'pause_period': config.pause_period,
            'jabberwocky_mode': config.jabberwocky_mode,
            'heartbeat': config.heartbeat,
            'heartbeat_margin': config.heartbeat_margin,

            # Form parameters
            'gender_choices': remap_choices(GENDER_CHOICES),
            'education_level_choices': remap_choices(EDUCATION_LEVEL_CHOICES),
            'job_type_choices': remap_choices(JOB_TYPE_CHOICES),

            # Experiment costs
            'experiment_work': config.experiment_work,
            'training_work': config.training_work,
            'tree_cost': config.tree_cost,
            'base_credit': config.base_credit,

            # Languages
            'default_language': DEFAULT_LANGUAGE,
            'supported_languages': remap_choices(LANGUAGE_CHOICES),
            'other_language': OTHER_LANGUAGE,

            # Server version
            'version': settings.VERSION,
        })


class Stats(views.APIView):
    """
    Public descriptive statistics about the data, with a cooled-down update.
    """

    COOLDOWN_PERIOD = timedelta(minutes=3)
    stats = None
    permission_classes = (
        # Anybody can read
        C(WantsSafe) |
        # Forcing the update is only for admins
        (C(WantsPost) & C(IsAdmin)),
    )

    def __init__(self, *args, **kwargs):
        super(Stats, self).__init__(*args, **kwargs)
        if (self.stats is None or
                now() - self.COOLDOWN_PERIOD > self.stats['updated']):
            self.update()

    @classmethod
    def update(cls):
        cls.stats = {
            'updated': now(),
            'mean_errs_per_profile': Sentence.mean_errs_per_profile(),
            'mean_read_time_proportion_per_profile':
                Sentence.mean_read_time_proportion_per_profile(),
            'mean_write_time_proportion_per_profile':
                Sentence.mean_write_time_proportion_per_profile(),
            'profiles_word_spans': Profile.word_spans()
        }

    def get(self, request, format=None):
        """Descriptive statistics about the data, with cooled-down update."""
        if now() - self.COOLDOWN_PERIOD > self.stats['updated']:
            self.update()
        return Response(self.stats)

    def post(self, request, format=None):
        """Force update of the statistics, admin-only."""
        self.update()
        return Response(self.stats)


class TreeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Tree list and detail, read only.
    """
    queryset = Tree.objects.all()
    serializer_class = TreeSerializer
    filter_class = TreeFilter
    filter_backends = (filters.DjangoFilterBackend,)

    PRIORITY_SHAPING = 'priority_shaping'

    @detail_route(methods=['put'],
                  permission_classes=[C(IsAuthenticated) & C(HasProfile)])
    @transaction.atomic()
    def heartbeat(self, request, pk=None, format=None):
        profile = self.request.user.profile
        timeout = GistsConfiguration.get_solo().heartbeat_timeout

        # self.get_object() doesn't let us use select_for_update(), which we
        # need to lock this tree for the duration of the view. So we directly
        # use django's get_object_or_404 with self.check_object_permissions().
        tree = get_object_or_404(self.get_queryset().select_for_update(),
                                 pk=pk)
        self.check_object_permissions(self.request, tree)

        if (tree.profile_lock is None or tree.profile_lock.id != profile.id
                or tree.profile_lock_heartbeat < now() - timeout):
            raise PermissionDenied('tree is not locked by requesting profile')

        tree.profile_lock_heartbeat = now()
        tree.save()
        return Response({'status': 'tree lock heartbeaten'})

    def filter_branches_count_lte(self, queryset, value):
        qs = queryset.annotate(branches_count=Count('root__children'))
        return qs.filter(branches_count__lte=value)

    def filter_shortest_branch_depth_lte(self, queryset, value):
        pks = [tree.pk for tree in queryset
               if tree.shortest_branch_depth <= value]
        return queryset.filter(pk__in=pks)

    def filter_shape(self, queryset):
        config = GistsConfiguration.get_solo()
        # Can't be full
        queryset = queryset\
            .annotate(sentences_count=Count('sentences'))\
            .filter(sentences_count__lte=config.target_branch_count
                    * config.target_branch_depth + 1)
        # Can't exceed width
        queryset = self.filter_branches_count_lte(
            queryset, config.target_branch_count)
        # Can't exceed max depth on all branches (but can reach it on all
        # branches: if the target width isn't reached but all existing branches
        # are at maximum length, you can still start a new branch)
        queryset = self.filter_shortest_branch_depth_lte(
            queryset, config.target_branch_depth)
        return queryset

    def has_boolean_param(self, params, name):
        return name in params and params.get(name).lower() == 'true'

    @list_route(permission_classes=[C(IsAuthenticated) & C(HasProfile)])
    def random_tree(self, request, format=None):
        tree = None
        queryset = self.filter_queryset(self.get_queryset())

        # Look for shaped trees first, if asked to
        if self.has_boolean_param(request.query_params, self.PRIORITY_SHAPING):
            shaped_pks = self.filter_shape(queryset)\
                .values_list('pk', flat=True)
            if len(shaped_pks) > 0:
                tree = Tree.objects.get(pk=choice(shaped_pks))

        # Shaping wasn't requested, or no shaped trees were available
        if tree is None:
            pks = queryset.values_list('pk', flat=True)
            if len(pks) > 0:
                tree = Tree.objects.get(pk=choice(pks))

        serializer = self.get_serializer([tree] if tree is not None else [],
                                         many=True)
        return Response(serializer.data)

    @list_route(permission_classes=[C(IsAuthenticated) & C(HasProfile)])
    @transaction.atomic()
    def lock_random_tree(self, request, format=None):
        profile = self.request.user.profile
        timeout = GistsConfiguration.get_solo().heartbeat_timeout
        tree = None

        free_qs = self.filter_queryset(self.get_queryset())\
            .select_for_update()\
            .filter(root__isnull=False)\
            .annotate(last_sentence=Max('sentences__created'))\
            .filter(Q(profile_lock_heartbeat__lt=now() - timeout)
                    | Q(last_sentence__gt=F('profile_lock_heartbeat')))

        # Look for free shaped trees first, if asked to
        if self.has_boolean_param(request.query_params, self.PRIORITY_SHAPING):
            shaped_free_pks = self.filter_shape(free_qs)\
                .values_list('pk', flat=True)
            if len(shaped_free_pks) > 0:
                tree = Tree.objects.get(pk=choice(shaped_free_pks))

        # Shaping wasn't requested, or no free shaped trees were available
        if tree is None:
            free_pks = free_qs.values_list('pk', flat=True)
            if len(free_pks) > 0:
                tree = Tree.objects.get(pk=choice(free_pks))

        # If we found something, lock it
        if tree is not None:
            tree.profile_lock = profile
            tree.profile_lock_heartbeat = now()
            tree.save()
            trees = [tree]
        else:
            trees = []

        serializer = self.get_serializer(trees, many=True)
        return Response(serializer.data)


class SentenceViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
    Sentence list and detail, unauthenticated read, authenticated creation.
    """
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer
    permission_classes = (
        # Anybody can read
        C(WantsRetrieve) | C(WantsList) |
        # Creation needs authentication with profile
        (C(WantsCreate) & C(IsAuthenticated) & C(HasProfile)),
    )
    ordering = ('-created',)

    @classmethod
    def obtain_empty_tree(cls):
        trees = Tree.objects.annotate(sentences_count=Count('sentences'))
        return trees.filter(sentences_count=0).first() or Tree.objects.create()

    def perform_create(self, serializer):
        profile = self.request.user.profile

        parent = serializer.validated_data.get('parent')
        if parent is None:
            # We're creating a new tree, check we're staff
            # or have suggestion credit
            if not (profile.user.is_staff or profile.suggestion_credit > 0):
                raise PermissionDenied
            tree = self.obtain_empty_tree()
            tree_as_root = tree
        else:
            tree = parent.tree
            tree_as_root = None

        serializer.save(profile=profile, tree=tree, tree_as_root=tree_as_root)


class ProfileViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """
    Profile list and detail, unauthenticated read, authenticated creation
    and modification.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (
        # Anybody can read
        C(WantsRetrieve) | C(WantsList) |
        # Other operations need authentication
        (C(IsAuthenticated) &
         # Creating is only if you have no profile
         ((C(WantsCreate) & ~C(HasProfile)) |
          # Update is only for admin or owner
          (C(WantsUpdate) & (C(IsAdmin) | C(ObjUserIsSelf))))),
    )
    ordering = ('user__username',)

    @list_route(permission_classes=[C(IsAuthenticated) & C(HasProfile)])
    def me(self, request, format=None):
        serializer = ProfileSerializer(request.user.profile,
                                       context={'request': request})
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class QuestionnaireViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """Questionnaire list and detail, authenticated read,
    authenticated creation."""
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer
    permission_classes = (
        # All operations need authentication
        (C(IsAuthenticated) &
         # Reading is ok for all, since the queryset gets reduced to
         # the user's questionnaire (or all if the user is admin)
         (C(WantsRetrieve) | C(WantsList) |
          # Creation needs a profile without a questionnaire
          (C(WantsCreate) & C(HasProfile) & ~C(HasQuestionnaire)))),
    )
    ordering = ('-created',)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        elif is_user_authenticated_with_profile(user):
            return self.queryset.filter(profile=user.profile)

        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)


class WordSpanViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """Word-span list and detail, authenticated read,
    authenticated creation."""
    queryset = WordSpan.objects.all()
    serializer_class = WordSpanSerializer
    permission_classes = (
        # All operations need authentication
        (C(IsAuthenticated) &
         # Reading is ok for all, since the queryset gets reduced to
         # the user's word-span (or all if the user is admin)
         (C(WantsRetrieve) | C(WantsList) |
          # Creation needs a profile without a word-span
          (C(WantsCreate) & C(HasProfile) & ~C(HasWordSpan)))),
    )
    ordering = ('-created',)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        elif is_user_authenticated_with_profile(user):
            return self.queryset.filter(profile=user.profile)

        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """Comments list and detail, authenticated read, authenticated creation."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (
        # All operations need authentication
        (C(IsAuthenticated) &
         # Reading is ok for all, since the queryset gets reduced to
         # the user's comments (or all if the user is admin)
         (C(WantsRetrieve) | C(WantsList) |
          # Creation needs a profile
          (C(WantsCreate) & C(HasProfile)))),
    )
    ordering = ('-created',)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        elif is_user_authenticated_with_profile(user):
            return self.queryset.filter(profile=user.profile)

        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    User list and detail, unauthenticated read, and authenticated modification
    (everything if staff, only username if self).
    """
    queryset = User.objects.all()
    permission_classes = (
        # Anybody can read
        C(WantsRetrieve) | C(WantsList) |
        # Update is only for admin or self
        (C(WantsUpdate) & (C(IsAdmin) | C(ObjIsSelf))),
    )
    ordering = ('username',)

    @list_route(permission_classes=[IsAuthenticated])
    def me(self, request, format=None):
        serializer = PrivateUserSerializer(request.user,
                                           context={'request': request})
        return Response(serializer.data)

    def perform_update(self, serializer):
        """Allow changing the username.

        'is_active' and 'is_staff' are blocked here, and 'email' is not a
        writable field on the serializer. so nothing but the username can be
        changed."""

        user = self.request.user
        obj = self.get_object()
        data = serializer.validated_data

        is_active_change = ('is_active' in data and
                            obj.is_active != data['is_active'])
        is_staff_change = ('is_staff' in data and
                           obj.is_staff != data['is_staff'])

        if ((is_staff_change or is_active_change) and not user.is_staff):
            raise PermissionDenied("Non-staff user cannot change "
                                   "'is_staff' or 'is_active'")
        serializer.save()

    def get_serializer_class(self):
        user = self.request.user

        # Staff can see everything
        if user.is_staff:
            return PrivateUserSerializer

        # Self in detail view can see privately
        if (self.action == 'retrieve') or (self.action == 'update'):
            obj = self.get_object()
            if user == obj:
                return PrivateUserSerializer

        # The rest sees publicly
        return UserSerializer


class EmailAddressViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    Email adresses list and detail, authenticated (staff or self) read and
    destroy, authenticated (any) create.
    """
    queryset = EmailAddress.objects.all()
    serializer_class = EmailAddressSerializer
    permission_classes = (
        # All operations need authentication
        (C(IsAuthenticated) &
         # Reading is ok for all, since the queryset gets reduced to
         # the user's emails (or all if the user is admin)
         (C(WantsRetrieve) | C(WantsList) |
          # Creation is also ok for all
          C(WantsCreate) |
          # Update and destroy are restricted to admin and self
          (C(WantsUpdate) & (C(IsAdmin) | C(ObjUserIsSelf))) |
          (C(WantsDestroy) & (C(IsAdmin) | C(ObjUserIsSelf))))),
    )
    ordering = ('user__username',)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset

        return self.queryset.filter(user=user)

    @detail_route(methods=['post'],
                  permission_classes=[C(IsAuthenticated) & C(ObjUserIsSelf)])
    def verify(self, request, pk=None, format=None):
        email = self.get_object()
        email.send_confirmation(request)
        return Response({'status': "A verification email has been sent "
                         "to '{}', please follow the "
                         "instructions in it".format(email.email)})

    def perform_create(self, serializer):
        """Send a confirmation email to the new address."""
        serializer.save(user=self.request.user)
        if not serializer.instance.verified:
            serializer.instance.send_confirmation(self.request)

    def perform_update(self, serializer):
        """Send a confirmation email to the new address."""
        serializer.save()
        if not serializer.instance.verified:
            serializer.instance.send_confirmation(self.request)

    def perform_destroy(self, instance):
        """Prevent deleting a primary address if it's not the last one."""
        other_emails = instance.user.emailaddress_set.exclude(pk=instance.pk)
        if other_emails.count() > 0:
            if instance.primary:
                raise PermissionDenied("Can't delete a primary address if "
                                       "it's not the last one")
        else:
            instance.user.email = ""
            instance.user.save()
        instance.delete()
