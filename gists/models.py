from django.db import models
from django.core.validators import (MinValueValidator, MaxValueValidator,
                                    MinLengthValidator)
from django.conf import settings
import networkx as nx
import numpy as np
from numpy.random import shuffle

from solo.models import SingletonModel
from .utils import memoize, levenshtein


DEFAULT_LANGUAGE = 'english'
OTHER_LANGUAGE = 'other'
LANGUAGE_CHOICES = sorted(
    [('french', 'French'),
     ('english', 'English'),
     ('spanish', 'Spanish'),
     ('italian', 'Italian'),
     ('german', 'German'),
     ('other', 'Other')],
    key=lambda l: l[1])
BUCKET_CHOICES = sorted(
    [('training', 'Training'),
     ('experiment', 'Experiment'),
     ('game', 'Game')],
    key=lambda b: b[1])
GENDER_CHOICES = [('female', 'Female'),
                  ('male', 'Male'),
                  ('other', 'Other')]
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
    base_credit = models.PositiveIntegerField(
        default=settings.DEFAULT_BASE_CREDIT)

    target_branch_count = models.PositiveIntegerField(
        default=settings.DEFAULT_TARGET_BRANCH_COUNT,
        validators=[MinValueValidator(1)])
    target_branch_depth = models.PositiveIntegerField(
        default=settings.DEFAULT_TARGET_BRANCH_DEPTH,
        validators=[MinValueValidator(2)])

    experiment_work = models.PositiveIntegerField(
        default=settings.DEFAULT_EXPERIMENT_WORK,
        validators=[MinValueValidator(1)])
    training_work = models.PositiveIntegerField(
        default=settings.DEFAULT_TRAINING_WORK,
        validators=[MinValueValidator(1)])

    reading_span_words_count = models.PositiveSmallIntegerField(
        default=settings.DEFAULT_READING_SPAN_WORDS_COUNT,
        validators=[MinValueValidator(3)])
    reading_span_trials_count = models.PositiveSmallIntegerField(
        default=settings.DEFAULT_READING_SPAN_TRIALS_COUNT,
        validators=[MinValueValidator(3)])

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
    text = models.CharField(max_length=5000)
    time_proportion = models.FloatField(validators=[MinValueValidator(0),
                                                    MaxValueValidator(1)])
    time_allotted = models.FloatField(validators=[MinValueValidator(0)])
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=100)
    bucket = models.CharField(choices=BUCKET_CHOICES, max_length=100)

    levenshtein = memoize(levenshtein)

    class Meta:
        ordering = ('-created',)

    @classmethod
    def mean_time_proportion_per_profile(cls):
        profiles_means = Sentence.objects.values('profile').annotate(
            mean=models.Avg('time_proportion')).order_by()

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
    def time_used(self):
        return self.time_allotted * self.time_proportion

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
    profiles = models.ManyToManyField('Profile', through='Sentence',
                                      through_fields=('tree', 'profile'),
                                      related_name='trees')

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

        edges = [(e['source'], e['target']) for e in self.network_edges]
        graph = nx.DiGraph(edges)
        heads = self.root.children.values_list('pk', flat=True)
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
    def reading_spans(cls):
        spans = np.array(Profile.objects
                         .filter(reading_span__isnull=False)
                         .values_list('reading_span__span', flat=True))
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

    @property
    def reformulations_count(self):
        n_created = self.sentences.filter(parent=None).count()
        return self.sentences.count() - n_created


class Questionnaire(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    profile = models.OneToOneField('Profile')

    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(3),
                                                       MaxValueValidator(120)])
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)

    naive = models.BooleanField(default=True)
    naive_detail = models.CharField(max_length=500, blank=True, default="")

    job_type = models.CharField(max_length=5, choices=JOB_TYPE_CHOICES)
    job_freetext = models.CharField(max_length=500,
                                    validators=[MinLengthValidator(5)])


class ReadingSpan(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    profile = models.OneToOneField('Profile', related_name="reading_span")
    words_count = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(3)])
    span = models.FloatField(validators=[MinValueValidator(0)])
