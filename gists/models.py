from django.db import models


class Sentence(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('auth.User', related_name='sentences')
    text = models.CharField(max_length=5000)

    class Meta:
        ordering = ('created',)
