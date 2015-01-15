from django.db import models


class Sentence(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('auth.User', related_name='sentences')
    parent = models.ForeignKey('Sentence', related_name='children',
                               null=True)
    text = models.CharField(max_length=5000)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        max_length = 20
        length = len(self.text)
        trunc, post = (max_length - 3, '...') if length > max_length else (length, '')
        string = "<Sentence {} by '{}': '{}'>".format(
            self.id, self.author.username, self.text[:trunc] + post)
        return string
