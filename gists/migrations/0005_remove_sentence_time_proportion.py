# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gists', '0004_auto_20150604_1206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sentence',
            name='time_proportion',
        ),
    ]
