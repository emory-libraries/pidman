# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pid', '0004_domain_hierarchy_mptt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='policy',
            field=models.ForeignKey(blank=True, to='pid.Policy', help_text=b'Policy statement for pids in this domain', null=True),
        ),
        migrations.AlterIndexTogether(
            name='pid',
            index_together=set([('updated_at', 'policy', 'editor', 'creator', 'ext_system', 'domain')]),
        ),
        migrations.AlterIndexTogether(
            name='target',
            index_together=set([('proxy', 'pid')]),
        ),
    ]
