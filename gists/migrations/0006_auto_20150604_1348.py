# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('gists', '0005_remove_sentence_time_proportion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sentence',
            name='time_used',
        ),
        migrations.AddField(
            model_name='sentence',
            name='time_proportion',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], default=0),
            preserve_default=False,
        ),
    ]
