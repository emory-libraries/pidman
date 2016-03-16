import sys
from django import db
import subprocess
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

        
        migrate(self)

def migrate(self):
    db_postgres = db.connections.databases['pg']['NAME']
    host_postgres = db.connections.databases['pg']['HOST']
    user_postgres = db.connections.databases['pg']['USER']
    pass_postgres = db.connections.databases['pg']['PASSWORD']

    db_mysql = db.connections.databases['default']['NAME']
    host_mysql = db.connections.databases['default']['HOST']
    user_mysql = db.connections.databases['default']['USER']
    pass_mysql = db.connections.databases['default']['PASSWORD']


    subprocess.call(['pidman/scripts/persis_postgres_dump.sh', '-D', db_postgres, '-h', host_postgres, '-u', user_postgres])
    subprocess.call(['pidman/scripts/persis_mysql_load.sh', '-h', host_mysql, '-u', user_mysql, '-p', pass_mysql])


    

