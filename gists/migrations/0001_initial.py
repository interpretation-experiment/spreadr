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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('mothertongue', models.CharField(choices=[('german', 'Deutsch'), ('english', 'English'), ('spanish', 'Español'), ('french', 'Français'), ('italian', 'Italiano'), ('other', 'Other')], max_length=100)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sentence',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=5000)),
                ('language', models.CharField(choices=[('german', 'Deutsch'), ('english', 'English'), ('spanish', 'Español'), ('french', 'Français'), ('italian', 'Italiano'), ('other', 'Other')], max_length=100)),
                ('parent', models.ForeignKey(null=True, related_name='children', to='gists.Sentence')),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('profiles', models.ManyToManyField(related_name='trees', through='gists.Sentence', to='gists.Profile')),
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
