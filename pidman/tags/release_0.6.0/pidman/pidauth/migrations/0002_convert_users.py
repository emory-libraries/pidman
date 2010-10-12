from south.db import db
from django.contrib.auth.models import User as DjangoUser
from django.db import models

class Migration:
    
    no_dry_run = True

    def forwards(self, orm):
        for user in orm.User.objects.all():
            duser, created = DjangoUser.objects.get_or_create(username=user.username)
            duser.first_name = user.first
            duser.last_name = user.last
            duser.email = user.email
            duser.password = user.password # straight copy of md5 hash
            duser.is_staff = True
            duser.is_active = True
            duser.is_superuser = user.is_superuser
            duser.save()
    
    
    def backwards(self, orm):
        # no effective way to delete the created data
        pass
    
    
    models = {
        'pidauth.role': {
            'Meta': {'db_table': "u'roles'"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'role': ('models.CharField', [], {'max_length': '64'}),
            'updated_at': ('models.DateTimeField', [], {'auto_now': 'True'})
        },
        'pidauth.domain': {
            'Meta': {'db_table': "u'domains'"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255', 'unique': 'True'}),
            'updated_at': ('models.DateTimeField', [], {'auto_now': 'True'})
        },
        'pidauth.user': {
            'Meta': {'db_table': "u'users'"},
            'email': ('models.EmailField', [], {'max_length': '320', 'unique': 'True'}),
            'first': ('models.CharField', [], {'max_length': '127'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_superuser': ('models.BooleanField', [], {}),
            'last': ('models.CharField', [], {'max_length': '127'}),
            'password': ('models.CharField', [], {'max_length': '150'}),
            'updated_at': ('models.DateTimeField', [], {'auto_now': 'True'}),
            'username': ('models.CharField', [], {'max_length': '32', 'unique': 'True'})
        },
        'pidauth.permission': {
            'Meta': {'db_table': "u'permissions'"},
            'domain': ('models.ForeignKey', ['Domain'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'role': ('models.ForeignKey', ['Role'], {}),
            'user': ('models.ForeignKey', ['User'], {})
        }
    }
    
    complete_apps = ['pidauth']
