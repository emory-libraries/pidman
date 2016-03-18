import sys
from distutils.util import strtobool
from django.db import transaction
from django.db.utils import IntegrityError
from django.core import serializers
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, Permission
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType


from django.contrib.humanize.templatetags.humanize import intcomma

import progressbar
from tabulate import tabulate

from pidman.pid import models as pid_models


class Command(BaseCommand):
    help = '''Migrate models from an old database to the current one.
    Expects a secondary database configured with the name 'pg'.
    Removes any conflicting models, and then copies models from the
    'pg' database to the configured 'default' database.'''

    # common django models, auth
    common_models = [ContentType, Permission, Group, User]

    # all pid related models
    pid_models = [pid_models.ExtSystem, pid_models.Proxy,
        pid_models.Policy, pid_models.Domain, pid_models.Pid,
        pid_models.Target]

    log_models = [LogEntry]

    # by default, migrate everything
    models_to_migrate = common_models + pid_models + log_models

    src_db = 'pg'
    dest_db = 'default'
    chunk_size = 3000

    def add_arguments(self, parser):
        parser.add_argument('-s', '--summary', default=False,
            action='store_true', help='Display summary information only')
        parser.add_argument('-n', '--num-per-chunk', default=self.chunk_size,
            help='Number of items to process per chunk (default: %(default)s)')
        # options to only migrate/report on specific sets of models
        parser.add_argument('--auth', action='store_true', default=False,
            help='Sync/summarize auth models (users, groups, permissions)')
        parser.add_argument('--pids', action='store_true', default=False,
            help='Sync/summarize all pid related models')
        parser.add_argument('--logs', action='store_true', default=False,
            help='Sync/summarize admin log entry models')


    def handle(self, *args, **options):
        # make sure db migrations are current
        call_command('migrate')

        # if specified, restrict which models to sync
        if options['auth'] or options['pids'] or options['logs']:
            self.models_to_migrate = []
            if options['auth']:
                self.models_to_migrate += self.common_models
            if options['pids']:
                self.models_to_migrate += self.pid_models
            if options['logs']:
                self.models_to_migrate += self.log_models

        # summarize model counts across the dbs
        self.summary()
        # if summary only was requested, exit
        if options['summary']:
            return

        # use django models to migrate data between dbs
        for model in self.models_to_migrate:
            self.batch_migrate(model)

        # special case: re-run pid sequence migration if pids were synced
        if pid_models.Pid in self.models_to_migrate:
            self.stdout.write('Re-running pid sequence migration')
            # migrate back so sequence can be re-run
            call_command('migrate', 'pid', '0001', '--fake')
            call_command('migrate', 'pid', '0002')

        self.summary()

    def summary(self):
        'Output totals of models by db and the differences'
        self.stdout.write(self.style.MIGRATE_HEADING('Model totals by database'))
        data = [[self.style.MIGRATE_LABEL(heading)  for heading in
            ['model', self.dest_db, self.src_db, 'difference']]]
        for model in self.models_to_migrate:
            data.append(self.model_db_counts(model))

            # also count many-to-many fields, to ensure they are copied
            for m2mfield in model._meta.many_to_many:
                m2m_model = getattr(model, m2mfield.name).through
                data.append(self.model_db_counts(m2m_model))

        self.stdout.write(tabulate(data, headers='firstrow'))

    def model_db_counts(self, model):
        'Model name, count in each db, and difference'
        from_count = model.objects.using(self.src_db).count()
        to_count = model.objects.using(self.dest_db).count()
        return [
            model._meta.verbose_name,
            intcomma(to_count, use_l10n=False),
            intcomma(from_count, use_l10n=False),
            intcomma(to_count - from_count, use_l10n=False)
        ]


    def batch_migrate(self, model, start=0):
        '''Migrate model data from one db to the other using django's
        capabability to save db records in an alternate database
        and bulk create.  If data is present in the destination db,
        it must be cleared out to avoid id conflicts; requests
        confirmation before deleting any records, and skips the model
        if delete is not approved.  Displays a progressbar
        when a model has more than 100 objects to migrate.
        '''
        # get a total of the objects to be copied
        count = model.objects.using(self.src_db).count()
        # nothing to do
        if not count:
            self.stdout.write('No %s objects to copy' % model._meta.verbose_name)
            return
        # remove from dest before copying
        if model.objects.using(self.dest_db).exists():
            dest_count = model.objects.using(self.dest_db).count()
            plural = ''
            if dest_count != 1:
                plural = 's'
            msg = 'Delete %s %s object%s from %s and load %d from %s?' % \
                    (dest_count, self.style.MIGRATE_LABEL(model._meta.verbose_name),
                     plural, self.style.WARNING(self.dest_db),
                     count, self.style.WARNING(self.src_db))
            if self.confirm(msg):
                model.objects.using(self.dest_db).all().delete()
            else:
                # if there are records that aren't deleted,
                # attempting to load will result in an integrity error,
                # so bail out
                return

        name = model._meta.verbose_name_plural
        if count == 1:
            name = model._meta.verbose_name
        self.stdout.write("Copying %s %s" % (intcomma(count, use_l10n=False), name))

        items = model.objects.using(self.src_db).all().order_by('pk')
        if count > 100:
            progress = progressbar.ProgressBar(max_value=count)
        else:
            progress = None

        item_count = 0
        # process in chunks, to handle models with lots of data
        for i in range(start, count, self.chunk_size):
            chunk_items = items[i:i+self.chunk_size]
            model.objects.using(self.dest_db).bulk_create(chunk_items)
            item_count += chunk_items.count()
            if progress:
                progress.update(item_count)

        # many-to-many fields are NOT handled by bulk create; check for
        # them and use the existing implicit through models to copy them
        # e.g. User.groups.through.objects.using('pg').all()

        # NOTE: this should only affect groups and user models; pid models
        # do not include any many-to-many relationships
        for m2mfield in model._meta.many_to_many:
            m2m_model = getattr(model, m2mfield.name).through
            self.batch_migrate(m2m_model)

    def confirm(self, question):
        'Display a message and get a command-line yes/no response as a boolean.'
        sys.stdout.write('%s [y/n] ' % question)
        while True:
            try:
                return strtobool(raw_input().lower())
            except ValueError:
                sys.stdout.write('Please respond with \'y\' or \'n\'.\n')

