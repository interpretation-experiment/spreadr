# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GistsConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('base_credit', models.PositiveIntegerField(default=0)),
                ('target_branch_count', models.PositiveIntegerField(default=6, validators=[django.core.validators.MinValueValidator(1)])),
                ('target_branch_depth', models.PositiveIntegerField(default=8, validators=[django.core.validators.MinValueValidator(2)])),
                ('experiment_work', models.PositiveIntegerField(default=50, validators=[django.core.validators.MinValueValidator(1)])),
                ('training_work', models.PositiveIntegerField(default=5, validators=[django.core.validators.MinValueValidator(1)])),
            ],
            options={
                'verbose_name': 'Gists Configuration',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('mothertongue', models.CharField(choices=[('english', 'English'), ('french', 'French'), ('german', 'German'), ('italian', 'Italian'), ('other', 'Other'), ('spanish', 'Spanish')], max_length=100)),
                ('trained_reformulations', models.BooleanField(default=False)),
                ('introduced_exp_home', models.BooleanField(default=False)),
                ('introduced_exp_play', models.BooleanField(default=False)),
                ('introduced_play_home', models.BooleanField(default=False)),
                ('introduced_play_play', models.BooleanField(default=False)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sentence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=5000)),
                ('language', models.CharField(choices=[('english', 'English'), ('french', 'French'), ('german', 'German'), ('italian', 'Italian'), ('other', 'Other'), ('spanish', 'Spanish')], max_length=100)),
                ('bucket', models.CharField(choices=[('experiment', 'Experiment'), ('game', 'Game'), ('training', 'Training')], max_length=100)),
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('profiles', models.ManyToManyField(to='gists.Profile', related_name='trees', through='gists.Sentence')),
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
        migrations.AddField(
            model_name='sentence',
            name='tree_as_root',
            field=models.OneToOneField(null=True, to='gists.Tree', related_name='root'),
            preserve_default=True,
        ),
    ]
