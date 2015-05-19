# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gists', '0003_auto_20150508_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='introduced_exp_home',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='introduced_exp_play',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='introduced_play_home',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='introduced_play_play',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
