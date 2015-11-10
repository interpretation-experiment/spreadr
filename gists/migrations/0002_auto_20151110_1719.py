# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gists', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='mothertongue',
            field=models.CharField(choices=[('english', 'English'), ('other', 'Other')], max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sentence',
            name='language',
            field=models.CharField(choices=[('english', 'English'), ('other', 'Other')], max_length=100),
            preserve_default=True,
        ),
    ]
