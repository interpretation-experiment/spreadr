# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('gists', '0002_auto_20150530_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentence',
            name='time',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], default=0),
            preserve_default=False,
        ),
    ]
