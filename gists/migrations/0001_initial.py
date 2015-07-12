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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('base_credit', models.PositiveIntegerField(default=0)),
                ('target_branch_count', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], default=6)),
                ('target_branch_depth', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(2)], default=8)),
                ('experiment_work', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], default=50)),
                ('training_work', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], default=5)),
                ('reading_span_words_count', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(3)], default=10)),
                ('reading_span_trials_count', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(3)], default=3)),
            ],
            options={
                'verbose_name': 'Gists Configuration',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('mothertongue', models.CharField(max_length=100, choices=[('english', 'English'), ('french', 'French'), ('german', 'German'), ('italian', 'Italian'), ('other', 'Other'), ('spanish', 'Spanish')])),
                ('trained_reformulations', models.BooleanField(default=False)),
                ('introduced_exp_home', models.BooleanField(default=False)),
                ('introduced_exp_play', models.BooleanField(default=False)),
                ('introduced_play_home', models.BooleanField(default=False)),
                ('introduced_play_play', models.BooleanField(default=False)),
                ('prolific_id', models.CharField(null=True, max_length=50)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('age', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(3), django.core.validators.MaxValueValidator(120)])),
                ('gender', models.CharField(max_length=100, choices=[('female', 'Female'), ('male', 'Male'), ('other', 'Other')])),
                ('informed', models.BooleanField(default=False)),
                ('informed_how', models.CharField(default='', blank=True, max_length=500)),
                ('informed_what', models.CharField(default='', blank=True, max_length=500)),
                ('job_type', models.CharField(max_length=5, choices=[('1', 'Student'), ('2', 'Manager'), ('3', 'Professional'), ('4', 'Technician or associate professional'), ('5', 'Clerical support worker'), ('6', 'Service or sales worker'), ('7', 'Skilled agricultural, forestry or fishery worker'), ('8', 'Craft or related trades worker'), ('9', 'Plant and machine operator, or assembler'), ('10', 'Elementary occupations'), ('11', 'Army'), ('-', 'Other')])),
                ('job_freetext', models.CharField(validators=[django.core.validators.MinLengthValidator(5)], max_length=500)),
                ('profile', models.OneToOneField(to='gists.Profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReadingSpan',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('words_count', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(3)])),
                ('span', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('profile', models.OneToOneField(to='gists.Profile', related_name='reading_span')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sentence',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('text', models.CharField(max_length=5000)),
                ('time_proportion', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('time_allotted', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('language', models.CharField(max_length=100, choices=[('english', 'English'), ('french', 'French'), ('german', 'German'), ('italian', 'Italian'), ('other', 'Other'), ('spanish', 'Spanish')])),
                ('bucket', models.CharField(max_length=100, choices=[('experiment', 'Experiment'), ('game', 'Game'), ('training', 'Training')])),
                ('parent', models.ForeignKey(to='gists.Sentence', related_name='children', null=True)),
                ('profile', models.ForeignKey(related_name='sentences', to='gists.Profile')),
            ],
            options={
                'ordering': ('-created',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tree',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('profiles', models.ManyToManyField(related_name='trees', to='gists.Profile', through='gists.Sentence')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sentence',
            name='tree',
            field=models.ForeignKey(related_name='sentences', to='gists.Tree'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sentence',
            name='tree_as_root',
            field=models.OneToOneField(to='gists.Tree', null=True, related_name='root'),
            preserve_default=True,
        ),
    ]
