# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('gists', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GistsConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_credit', models.PositiveIntegerField(default=2)),
                ('target_branch_count', models.PositiveIntegerField(default=5, validators=[django.core.validators.MinValueValidator(1)])),
                ('target_branch_depth', models.PositiveIntegerField(default=10, validators=[django.core.validators.MinValueValidator(2)])),
            ],
            options={
                'verbose_name': 'Gists Configuration',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='profile',
            name='mothertongue',
            field=models.CharField(choices=[('english', 'English'), ('french', 'French'), ('german', 'German'), ('italian', 'Italian'), ('other', 'Other'), ('spanish', 'Spanish')], max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sentence',
            name='language',
            field=models.CharField(choices=[('english', 'English'), ('french', 'French'), ('german', 'German'), ('italian', 'Italian'), ('other', 'Other'), ('spanish', 'Spanish')], max_length=100),
            preserve_default=True,
        ),
    ]
