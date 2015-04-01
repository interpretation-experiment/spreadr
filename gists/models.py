from django.db import models
from django.conf import settings

from solo.models import SingletonModel


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


class GistsConfiguration(SingletonModel):
    base_credit = models.IntegerField(default=settings.DEFAULT_BASE_CREDIT)
    target_branch_count = models.IntegerField(
        default=settings.DEFAULT_TARGET_BRANCH_COUNT)
    target_branch_length = models.IntegerField(
        default=settings.DEFAULT_TARGET_BRANCH_LENGTH)

    @property
    def tree_cost(self):
        return self.target_branch_count * self.target_branch_length

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
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=100)

    class Meta:
        ordering = ('-created',)

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
    def distinct_profiles(self):
        return self.profiles.distinct()


class Profile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField('auth.User')
    mothertongue = models.CharField(choices=LANGUAGE_CHOICES, max_length=100)

    @property
    def distinct_trees(self):
        return self.trees.distinct()

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
        cost = config.tree_cost

        n_created = self.sentences.filter(parent=None).count()
        n_transformed = self.sentences.count() - n_created

        return cost - (n_transformed % cost)
