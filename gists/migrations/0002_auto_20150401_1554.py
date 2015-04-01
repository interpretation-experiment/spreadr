# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gists', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GistsConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('base_credit', models.IntegerField(default=2)),
                ('target_branch_count', models.IntegerField(default=5)),
                ('target_branch_length', models.IntegerField(default=10)),
            ],
            options={
                'verbose_name': 'Gists Configuration',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='profile',
            name='mothertongue',
            field=models.CharField(max_length=100, choices=[('english', 'English'), ('french', 'French'), ('german', 'German'), ('italian', 'Italian'), ('other', 'Other'), ('spanish', 'Spanish')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sentence',
            name='language',
            field=models.CharField(max_length=100, choices=[('english', 'English'), ('french', 'French'), ('german', 'German'), ('italian', 'Italian'), ('other', 'Other'), ('spanish', 'Spanish')]),
            preserve_default=True,
        ),
    ]
