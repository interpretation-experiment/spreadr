from django.db import models
from django.conf import settings


LANGUAGE_CHOICES = sorted(
    [('french', 'Français'),
     ('english', 'English'),
     ('spanish', 'Español'),
     ('italian', 'Italiano'),
     ('german', 'Deutsch'),
     ('other', 'Other')],
    key=lambda l: l[1])


class Sentence(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    tree = models.ForeignKey('Tree', related_name='sentences')
    profile = models.ForeignKey('Profile', related_name='sentences')
    parent = models.ForeignKey('Sentence', related_name='children', null=True)
    text = models.CharField(max_length=5000)
    language = models.CharField(choices=LANGUAGE_CHOICES, max_length=100)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        max_length = 20
        length = len(self.text)
        trunc, post = ((max_length - 3, '...') if length > max_length
                       else (length, ''))
        string = "<Sentence {} by '{}': '{}'>".format(
            self.id, self.profile.user.username, self.text[:trunc] + post)
        return string


class Tree(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    root = models.OneToOneField('Sentence', related_name='tree_as_root',
                                null=True)
    profile = models.ForeignKey('Profile', related_name='created_trees')


class Profile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField('auth.User')
    mothertongue = models.CharField(choices=LANGUAGE_CHOICES, max_length=100)

    @property
    def suggestion_credit(self):
        base = settings.BASE_CREDIT
        cost = settings.SUGGESTION_COST

        n_created = self.created_trees.count()
        n_transformed = self.sentences.count() - n_created

        return base + (n_transformed // cost) - n_created
