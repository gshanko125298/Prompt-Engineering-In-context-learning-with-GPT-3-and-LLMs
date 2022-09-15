# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields
import django.utils.timezone
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('name', models.CharField(max_length=32)),
                ('client_id', models.CharField(max_length=32)),
                ('client_secret', models.CharField(max_length=32)),
                ('auth_url', models.URLField()),
                ('token_url', models.URLField()),
                ('revoke_url', models.URLField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('name', models.CharField(max_length=32)),
                ('access_token', models.CharField(max_length=64, blank=True)),
                ('expires_in', models.IntegerField(default=0)),
                ('refresh_token', models.CharField(max_length=128, blank=True)),
                ('token_type', models.CharField(default=b'bearer', max_length=32)),
                ('provider', models.ForeignKey(to='oauthclient.Provider')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TokenRestrictedTo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=256)),
                ('token', models.ForeignKey(to='oauthclient.Token')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
