import re
from datetime import timedelta, datetime
try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.now

from django.db import models
from django.core.validators import (MinValueValidator, MaxValueValidator,
                                    MinLengthValidator)
from django.conf import settings
import networkx as nx
import numpy as np
from numpy.random import shuffle

from solo.models import SingletonModel
from .utils import memoize, levenshtein
from .validators import SpellingValidator, PunctuationValidator


DEFAULT_LANGUAGE = 'english'
OTHER_LANGUAGE = 'other'
LANGUAGE_CHOICES = sorted(
    [(DEFAULT_LANGUAGE, 'English'),
     (OTHER_LANGUAGE, 'Other')],
    key=lambda l: l[1])
BUCKET_CHOICES = sorted(
    [('training', 'Training'),
     ('experiment', 'Experiment'),
     ('game', 'Game')],
    key=lambda b: b[1])
GENDER_CHOICES = [('female', 'Female'),
                  ('male', 'Male'),
                  ('other', 'Other')]

# Gross levels of
# https://en.wikipedia.org/wiki/International_Standard_Classification_of_Education#ISCED_2011_levels.2C_categories.2C_and_sub-categories
EDUCATION_LEVEL_CHOICES = [
    ('1', 'No schooling'),
    ('2', 'Incomplete primary'),
    ('3', 'Primary'),
    ('4', 'Lower secondary'),
    ('5', 'Upper secondary'),
    ('6', 'Post-secondary non-tertiary'),
    ('7', 'Short-cycle tertiary'),
    ('8', "Bachelor's or equivalent"),
    ('9', "Master's or equivalent"),
    ('10', "Doctoral or equivalent"),
    ('-', 'Other'),
]

# Gross levels of
# https://en.wikipedia.org/wiki/International_Standard_Classification_of_Occupations#The_ISCO-08_structure
JOB_TYPE_CHOICES = [
    ('1', 'Student'),
    ('2', 'Manager'),
    ('3', 'Professional'),
    ('4', 'Technician or associate professional'),
    ('5', 'Clerical support worker'),
    ('6', 'Service or sales worker'),
    ('7', 'Skilled agricultural, forestry or fishery worker'),
    ('8', 'Craft or related trades worker'),
    ('9', 'Plant and machine operator, or assembler'),
    ('10', 'Elementary occupations'),
    ('11', 'Army'),
    ('-', 'Other'),
]


class GistsConfiguration(SingletonModel):
    target_branch_depth = models.PositiveIntegerField(
        default=settings.DEFAULT_TARGET_BRANCH_DEPTH,
        validators=[MinValueValidator(2)])
    target_branch_count = models.PositiveIntegerField(
        default=settings.DEFAULT_TARGET_BRANCH_COUNT,
        validators=[MinValueValidator(1)])
    branch_probability = models.FloatField(
        default=settings.DEFAULT_BRANCH_PROBABILITY,
        validators=[MinValueValidator(0.1)])

    read_factor = models.FloatField(
        default=settings.DEFAULT_READ_FACTOR,
        validators=[MinValueValidator(0.01)])
    write_factor = models.FloatField(
        default=settings.DEFAULT_WRITE_FACTOR,
        validators=[MinValueValidator(0.01)])
    min_tokens = models.PositiveIntegerField(
        default=settings.DEFAULT_MIN_TOKENS,
        validators=[MinValueValidator(1)])
    pause_period = models.PositiveIntegerField(
        default=settings.DEFAULT_PAUSE_PERIOD,
        validators=[MinValueValidator(1)])
    jabberwocky_mode = models.BooleanField(
        default=settings.DEFAULT_JABBERWOCKY_MODE)

    experiment_work = models.PositiveIntegerField(
        default=settings.DEFAULT_EXPERIMENT_WORK,
        validators=[MinValueValidator(1)])
    training_work = models.PositiveIntegerField(
        default=settings.DEFAULT_TRAINING_WORK,
        validators=[MinValueValidator(1)])
    base_credit = models.PositiveIntegerField(
        default=settings.DEFAULT_BASE_CREDIT)

    @property
    def tree_cost(self):
        return self.target_branch_count * self.target_branch_depth

    def __unicode__(self):
        return "Gists Configuration"

    class Meta:
        verbose_name = "Gists Configuration"


class Sentence(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    tree = models.ForeignKey('Tree', related_name='sentences')
    profile = models.ForeignKey('Profile', related_name='sentences')
    parent = models.ForeignKey('Sentence', related_name='children', null=True)
    tree_as_root = models.OneToOneField('Tree', related_name='root', null=True)
    text = models.CharField(max_length=5000,
                            validators=[SpellingValidator(DEFAULT_LANGUAGE),
                                        PunctuationValidator()])
    read_time_proportion = models.FloatField(validators=[MinValueValidator(0),
                                                         MaxValueValidator(1)])
    read_time_allotted = models.FloatField(validators=[MinValueValidator(0)])
    write_time_proportion = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)])
    write_time_allotted = models.FloatField(validators=[MinValueValidator(0)])
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=100)
    bucket = models.CharField(choices=BUCKET_CHOICES, max_length=100)

    levenshtein = memoize(levenshtein)

    class Meta:
        ordering = ('-created',)

    @classmethod
    def bucket_counts(cls, queryset):
        return dict((bucket[0], queryset.filter(bucket=bucket[0]).count())
                    for bucket in BUCKET_CHOICES)

    @classmethod
    def mean_read_time_proportion_per_profile(cls):
        profiles_means = Sentence.objects.filter(
            parent__isnull=False).values('profile').annotate(
            mean=models.Avg('read_time_proportion')).order_by()

        means = {}
        for profile_mean in profiles_means:
            means[profile_mean['profile']] = profile_mean['mean']

        return means

    @classmethod
    def mean_write_time_proportion_per_profile(cls):
        profiles_means = Sentence.objects.filter(
            parent__isnull=False).values('profile').annotate(
            mean=models.Avg('write_time_proportion')).order_by()

        means = {}
        for profile_mean in profiles_means:
            means[profile_mean['profile']] = profile_mean['mean']

        return means

    @classmethod
    def mean_errs_per_profile(cls):
        texts = Sentence.objects.filter(
            parent__isnull=False).values('profile', 'text', 'parent__text')

        errs = {}
        for item in texts:
            profile = item['profile']
            if profile not in errs:
                errs[profile] = []
            distance = cls.levenshtein(item['parent__text'], item['text'])
            errs[profile].append(distance / len(item['parent__text']))

        for profile, pErrs in errs.items():
            errs[profile] = np.mean(pErrs)

        return errs

    @property
    def read_time_used(self):
        return self.read_time_allotted * self.read_time_proportion

    @property
    def write_time_used(self):
        return self.write_time_allotted * self.write_time_proportion

    def __str__(self):
        max_length = 20
        length = len(self.text)
        trunc, post = ((max_length - 3, '...') if length > max_length
                       else (length, ''))
        string = "{} by '{}': '{}'".format(
            self.id, self.profile.user.username, self.text[:trunc] + post)
        return string


class Tree(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_served = models.DateTimeField(
        default=datetime(year=2000, month=1, day=1))
    profiles = models.ManyToManyField('Profile', through='Sentence',
                                      through_fields=('tree', 'profile'),
                                      related_name='trees')

    SPACES = re.compile(' +')

    @classmethod
    def bucket_counts(cls, queryset):
        return dict((bucket[0],
                     queryset.filter(root__bucket=bucket[0]).count())
                    for bucket in BUCKET_CHOICES)

    @property
    def timedout(self):
        if self.sentences.count() == 0:
            # No root
            return False

        config = GistsConfiguration.get_solo()
        n_tokens = len(self.SPACES.split(self.root.text))
        timeout = timedelta(seconds=2 * n_tokens
                            * (config.read_factor + config.write_factor))
        return now() - self.last_served > timeout

    @property
    def network_edges(self):
        edges = self.sentences.values('pk', 'children')
        return [{'source': e['pk'], 'target': e['children']} for e in edges
                if e['pk'] is not None and e['children'] is not None]

    @property
    def shortest_branch_depth(self):
        # No root or nothing but root? Return fast
        sentences_count = self.sentences.count()
        if sentences_count <= 1:
            return sentences_count

        heads = self.root.children.values_list('pk', flat=True)
        edges = [(e['source'], e['target']) for e in self.network_edges]
        graph = nx.DiGraph(edges)
        all_depths = [nx.single_source_shortest_path_length(graph, h)
                      for h in heads]
        branch_depths = [1 + max(depths.values()) for depths in all_depths]
        return min(branch_depths)

    @property
    def distinct_profiles(self):
        return self.profiles.distinct().order_by()


class Profile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField('auth.User')

    mothertongue = models.CharField(choices=LANGUAGE_CHOICES, max_length=100)
    trained_reformulations = models.BooleanField(default=False)

    introduced_exp_home = models.BooleanField(default=False)
    introduced_exp_play = models.BooleanField(default=False)
    introduced_play_home = models.BooleanField(default=False)
    introduced_play_play = models.BooleanField(default=False)

    prolific_id = models.CharField(max_length=50, null=True)

    @classmethod
    def word_spans(cls):
        spans = np.array(Profile.objects
                         .filter(word_span__isnull=False)
                         .values_list('word_span__span', flat=True))
        shuffle(spans)
        return spans

    @property
    def distinct_trees(self):
        return self.trees.distinct().order_by()

    @property
    def suggestion_credit(self):
        config = GistsConfiguration.get_solo()
        base = config.base_credit
        cost = config.tree_cost

        n_created = self.sentences.filter(parent=None).count()
        n_transformed = self.sentences.count() - n_created

        return base + (n_transformed // cost) - n_created

    @property
    def next_credit_in(self):
        config = GistsConfiguration.get_solo()
        cost = config.tree_cost

        n_created = self.sentences.filter(parent=None).count()
        n_transformed = self.sentences.count() - n_created

        return cost - (n_transformed % cost)


class Questionnaire(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    profile = models.OneToOneField('Profile')

    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(3),
                                                       MaxValueValidator(120)])
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)

    informed = models.BooleanField(default=False)
    informed_how = models.CharField(max_length=500,
                                    validators=[MinLengthValidator(5)])
    informed_what = models.CharField(max_length=500,
                                     validators=[MinLengthValidator(5)])

    education_level = models.CharField(max_length=5,
                                       choices=EDUCATION_LEVEL_CHOICES)
    education_freetext = models.CharField(max_length=500,
                                          validators=[MinLengthValidator(5)])

    job_type = models.CharField(max_length=5, choices=JOB_TYPE_CHOICES)
    job_freetext = models.CharField(max_length=500,
                                    validators=[MinLengthValidator(5)])


class WordSpan(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    profile = models.OneToOneField('Profile', related_name="word_span")
    span = models.PositiveSmallIntegerField()
    score = models.PositiveSmallIntegerField()


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey('Profile', related_name='comments')

    email = models.EmailField()
    meta = models.CharField(max_length=5000)
    text = models.CharField(max_length=5000,
                            validators=[MinLengthValidator(5)])
