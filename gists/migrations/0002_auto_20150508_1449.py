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
            name='training_work',
            field=models.PositiveIntegerField(default=5, validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gistsconfiguration',
            name='base_credit',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
