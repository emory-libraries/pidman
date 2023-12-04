# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields

from pidman.pid.models import Domain


def rebuild_hierarchy(apps, schema_editor):
    # use mptt to (re)build hierarchy based on parent relationship
    # per https://github.com/django-mptt/django-mptt/issues/173
    Domain.objects.rebuild()


class Migration(migrations.Migration):

    dependencies = [
        ('pid', '0003_rm_invalidark_target_urlfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='level',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='domain',
            name='lft',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='domain',
            name='rght',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='domain',
            name='tree_id',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='domain',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='collections', blank=True, to='pid.Domain', null=True, on_delete=models.CASCADE),
        ),
        migrations.RunPython(rebuild_hierarchy, migrations.RunPython.noop)
    ]

