from datetime import timedelta
try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now

from django.contrib.auth.models import User
from django.db.models import Count
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

from gists.filters import TreeFilter
from gists.models import (Sentence, Tree, Profile, Questionnaire,
                          WordSpan, GistsConfiguration,
                          LANGUAGE_CHOICES, OTHER_LANGUAGE, DEFAULT_LANGUAGE,
                          GENDER_CHOICES, JOB_TYPE_CHOICES,)
from gists.serializers import (SentenceSerializer, TreeSerializer,
                               ProfileSerializer, QuestionnaireSerializer,
                               WordSpanSerializer,
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
            'version': settings.VERSION,

            'supported_languages': remap_choices(LANGUAGE_CHOICES),
            'other_language': OTHER_LANGUAGE,
            'default_language': DEFAULT_LANGUAGE,

            'base_credit': config.base_credit,
            'target_branch_count': config.target_branch_count,
            'target_branch_depth': config.target_branch_depth,
            'experiment_work': config.experiment_work,
            'training_work': config.training_work,
            'tree_cost': config.tree_cost,
            'word_span_words_count': config.word_span_words_count,
            'word_span_trials_count': config.word_span_trials_count,

            'gender_choices': remap_choices(GENDER_CHOICES),
            'job_type_choices': remap_choices(JOB_TYPE_CHOICES),
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
    def obtain_free_tree(cls):
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
            tree = self.obtain_free_tree()
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
          # Creation needs a profile without a questionnaire
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


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    User list and detail, unauthenticated read, authenticated and modification
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
        serializer = UserSerializer(request.user, context={'request': request})
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
        if self.action == 'retrieve':
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
    def verify(self, request, pk=None):
        email = get_object_or_404(self.queryset, pk=pk)
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
