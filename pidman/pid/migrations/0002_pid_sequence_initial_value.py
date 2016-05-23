# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from pidman.pid.noid import decode_noid
from pidman.pid import models as pid_models


def pid_sequence_lastvalue(apps, schema_editor):
    # if the database has existing pids, update the sequence last value
    # so it will start minting pids starting after the current set
    Pid = apps.get_model("pid", "Pid")
    Sequence = apps.get_model("sequences", "Sequence")

    if Pid.objects.count():
        print Pid.objects.count()
        max_noid = Pid.objects.all() \
                      .aggregate(models.Max('pid')).values()[0]

        last_val = decode_noid(max_noid)
        pid_seq, created = Sequence.objects.get_or_create(name=pid_models.Pid.SEQUENCE_NAME)
        pid_seq.last = last_val
        pid_seq.save()

def remove_pid_sequence(apps, schema_editor):
    Sequence = apps.get_model("sequences", "Sequence")
    Sequence.objects.get(name=pid_models.Pid.SEQUENCE_NAME).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('pid', '0001_initial'),
        ('sequences', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(pid_sequence_lastvalue,
                             remove_pid_sequence),
    ]
