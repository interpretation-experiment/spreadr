# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gists', '0002_auto_20150508_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentence',
            name='bucket',
            field=models.CharField(choices=[('experiment', 'Experiment'), ('game', 'Game'), ('training', 'Training')], max_length=100),
            preserve_default=True,
        ),
    ]
