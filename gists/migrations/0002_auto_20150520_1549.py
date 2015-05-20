# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gists', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='introduced_exp_home',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='introduced_exp_play',
        ),
        migrations.AddField(
            model_name='profile',
            name='introduced_exp_doing_home',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='introduced_exp_doing_play',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='introduced_exp_training_home',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='introduced_exp_training_play',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
