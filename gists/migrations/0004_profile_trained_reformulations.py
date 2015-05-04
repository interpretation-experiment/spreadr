# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gists', '0003_auto_20150504_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='trained_reformulations',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
