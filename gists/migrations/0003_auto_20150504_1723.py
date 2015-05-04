# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('gists', '0002_auto_20150401_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='gistsconfiguration',
            name='experiment_work',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], default=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gistsconfiguration',
            name='base_credit',
            field=models.PositiveIntegerField(default=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gistsconfiguration',
            name='target_branch_count',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], default=6),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='gistsconfiguration',
            name='target_branch_depth',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(2)], default=8),
            preserve_default=True,
        ),
    ]
