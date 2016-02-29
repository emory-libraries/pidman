import sys
from django.db import transaction
from django.db.utils import IntegrityError
from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, Permission
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

import progressbar

from pidman.pid import models as pid_models


class Command(BaseCommand):
    help = 'Migrate data from an old database'

    # NOTE: currently expects old postgres database to be configured
    # with name 'pg'

    # possibly add an option to only copy content created after
    # a specified date? or after latest data in current db?


    def handle(self, *args, **options):

        # TODO: should probably have some kind of summary count of models
        # in from/to dbs to compare before and after

        migrate(ContentType)
        migrate(Permission)
        migrate(Group)
        migrate(User)
        migrate(pid_models.ExtSystem)
        migrate(pid_models.Proxy)
        migrate(pid_models.Policy)
        migrate(pid_models.Domain)
        migrate_pids_with_targets()
        migrate(LogEntry)


# based on http://www.ofbrooklyn.com/2010/07/18/migrating-django-mysql-postgresql-easy-way/
def migrate(model, size=1000, start=0, fltr=None):
    # copying using natural keys to ensure we don't break
    # or mismatch related object associations
    # but note that it does seem to be slower

    from_db = 'pg'
    to_db = 'default'
    count = model.objects.using(from_db).count()
    # print "\n%s objects in model %s\n" % (count, model)
    print "\nCopying %s %s" % (count,
        model._meta.verbose_name_plural.title())

    if count > 100:
        progress = progressbar.ProgressBar(max_value=count)
    else:
        progress = None

    items = model.objects.using(from_db).all()
    if fltr is not None:
        items = items.filter(**fltr)
    item_count = 0

    # process each chunk in a transaction
    # (especially important when working with sqlite)
    with transaction.atomic():
        for i in range(start, count, size):

            original_data = items[i:i+size]
            original_data_json = serializers.serialize("json", original_data,
                use_natural_primary_keys=True, use_natural_foreign_keys=True)
            new_data = serializers.deserialize("json", original_data_json,
                                               using=to_db)
            for item in new_data:
                item.save(using=to_db)
                item_count += 1
                if progress:
                    progress.update(item_count)


def migrate_pids_with_targets(size=1000, start=0):
    from_db = 'pg'
    to_db = 'default'

    target_count = pid_models.Target.objects.using(from_db).count()
    pid_count = pid_models.Pid.objects.using(from_db).count()
    print "\nCopying %s pids and %s targets" % (pid_count, target_count)
    progress = progressbar.ProgressBar(max_value=pid_count + target_count)

    pids = pid_models.Pid.objects.using(from_db).all() \
                         .prefetch_related('target_set')

    pids = pids[:3000]

    item_count = 0
    with transaction.atomic():
        for i in range(start, target_count, size):

            original_data = pids[i:i+size]
            # natural keys work here, but it seems to be much slower
            pid_data_json = serializers.serialize("json", original_data,
                      use_natural_foreign_keys=True, use_natural_primary_keys=True)

            target_data_json = serializers.serialize('json',
                [t for p in original_data
                    for t in p.target_set.all()],
                  use_natural_foreign_keys=True, use_natural_primary_keys=True)

            # first migrate the pids
            new_pid_data = serializers.deserialize('json', pid_data_json,
                using=to_db)
            for item in new_pid_data:
                item.save(using=to_db)
                item_count += 1
                progress.update(item_count)

            # then migrate the associated targets
            new_target_data = serializers.deserialize("json", target_data_json,
                                               using=to_db)
            for item in new_target_data:
                item.save(using=to_db)
                item_count += 1
                progress.update(item_count)

