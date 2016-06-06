# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pid', '0002_pid_sequence_initial_value'),
    ]

    operations = [
        migrations.DeleteModel(
            name='InvalidArk',
        ),
        migrations.AlterField(
            model_name='target',
            name='uri',
            field=models.URLField(max_length=2048),
        ),
    ]
