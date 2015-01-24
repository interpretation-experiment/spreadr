from django.db import models


class Sentence(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    tree = models.ForeignKey('Tree', related_name='sentences')
    author = models.ForeignKey('Profile', related_name='sentences')
    parent = models.ForeignKey('Sentence', related_name='children', null=True)
    text = models.CharField(max_length=5000)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        max_length = 20
        length = len(self.text)
        trunc, post = (max_length - 3, '...') if length > max_length else (length, '')
        string = "<Sentence {} by '{}': '{}'>".format(
            self.id, self.author.user.username, self.text[:trunc] + post)
        return string


class Tree(models.Model):

    @property
    def authors(self):
        return set([s.author for s in self.sentences.all()])


class Profile(models.Model):
    user = models.OneToOneField('auth.User')

    @property
    def trees(self):
        return set([s.tree for s in self.sentences.all()])
