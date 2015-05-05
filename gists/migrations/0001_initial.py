# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GistsConfiguration',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('base_credit', models.PositiveIntegerField(default=1)),
                ('target_branch_count', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], default=6)),
                ('target_branch_depth', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(2)], default=8)),
                ('experiment_work', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], default=50)),
            ],
            options={
                'verbose_name': 'Gists Configuration',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('mothertongue', models.CharField(max_length=100, choices=[('english', 'English'), ('french', 'French'), ('german', 'German'), ('italian', 'Italian'), ('other', 'Other'), ('spanish', 'Spanish')])),
                ('trained_reformulations', models.BooleanField(default=False)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sentence',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=5000)),
                ('language', models.CharField(max_length=100, choices=[('english', 'English'), ('french', 'French'), ('german', 'German'), ('italian', 'Italian'), ('other', 'Other'), ('spanish', 'Spanish')])),
                ('bucket', models.CharField(max_length=100, choices=[('experiment', 'Experiment'), ('game', 'Game')])),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('profiles', models.ManyToManyField(through='gists.Sentence', to='gists.Profile', related_name='trees')),
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
