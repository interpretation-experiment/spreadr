# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('gists', '0003_sentence_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sentence',
            old_name='time',
            new_name='time_proportion',
        ),
        migrations.AddField(
            model_name='sentence',
            name='time_allotted',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0)], default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sentence',
            name='time_used',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0)], default=0),
            preserve_default=False,
        ),
    ]
