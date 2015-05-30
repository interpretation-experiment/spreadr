# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('gists', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gistsconfiguration',
            name='reading_span_trials_count',
            field=models.PositiveSmallIntegerField(default=3, validators=[django.core.validators.MinValueValidator(3)]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gistsconfiguration',
            name='reading_span_words_count',
            field=models.PositiveSmallIntegerField(default=10, validators=[django.core.validators.MinValueValidator(3)]),
            preserve_default=True,
        ),
    ]
