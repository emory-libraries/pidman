# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import pidman.pid.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(related_name='collections', db_column=b'parent_id', blank=True, to='pid.Domain', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExtSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=127)),
                ('key_field', models.CharField(max_length=127)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'External System',
            },
        ),
        migrations.CreateModel(
            name='Pid',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pid', models.CharField(default=pidman.pid.models.mint_noid, unique=True, max_length=255, editable=False)),
                ('name', models.CharField(max_length=1023, blank=True)),
                ('ext_system_key', models.CharField(max_length=1023, null=True, verbose_name=b'External system key', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Created')),
                ('type', models.CharField(max_length=25, choices=[(b'Ark', b'Ark'), (b'Purl', b'Purl')])),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name=b'Date Updated')),
                ('creator', models.ForeignKey(related_name='created', to=settings.AUTH_USER_MODEL)),
                ('domain', models.ForeignKey(to='pid.Domain')),
                ('editor', models.ForeignKey(related_name='edited', to=settings.AUTH_USER_MODEL)),
                ('ext_system', models.ForeignKey(verbose_name=b'External system', blank=True, to='pid.ExtSystem', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Created')),
                ('commitment', models.TextField(verbose_name=b'Commitment Statement')),
                ('title', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Policies',
            },
        ),
        migrations.CreateModel(
            name='Proxy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=127)),
                ('transform', models.CharField(max_length=127)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Proxies',
            },
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('noid', models.CharField(max_length=255, editable=False)),
                ('uri', models.CharField(max_length=2048)),
                ('qualify', models.CharField(default=b'', max_length=255, verbose_name=b'Qualifier', blank=True)),
                ('active', models.BooleanField(default=True)),
                ('pid', models.ForeignKey(to='pid.Pid')),
                ('proxy', models.ForeignKey(blank=True, to='pid.Proxy', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='pid',
            name='policy',
            field=models.ForeignKey(blank=True, to='pid.Policy', null=True),
        ),
        migrations.AddField(
            model_name='domain',
            name='policy',
            field=models.ForeignKey(blank=True, to='pid.Policy', null=True),
        ),
        migrations.CreateModel(
            name='InvalidArk',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('pid.pid',),
        ),
        migrations.AlterUniqueTogether(
            name='target',
            unique_together=set([('pid', 'qualify')]),
        ),
    ]
