# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('mothertongue', models.CharField(max_length=100, choices=[('german', 'Deutsch'), ('english', 'English'), ('spanish', 'Español'), ('french', 'Français'), ('italian', 'Italiano'), ('other', 'Other')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sentence',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=5000)),
                ('language', models.CharField(max_length=100, choices=[('german', 'Deutsch'), ('english', 'English'), ('spanish', 'Español'), ('french', 'Français'), ('italian', 'Italiano'), ('other', 'Other')])),
                ('parent', models.ForeignKey(null=True, to='gists.Sentence', related_name='children')),
                ('profile', models.ForeignKey(to='gists.Profile', related_name='sentences')),
            ],
            options={
                'ordering': ('-created',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tree',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(to='gists.Profile', related_name='created_trees')),
                ('root', models.OneToOneField(null=True, to='gists.Sentence', related_name='tree_as_root')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sentence',
            name='tree',
            field=models.ForeignKey(to='gists.Tree', related_name='sentences'),
            preserve_default=True,
        ),
    ]
