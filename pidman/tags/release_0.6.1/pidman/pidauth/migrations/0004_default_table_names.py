
from south.db import db
from django.db import models
from pidman.pidauth.models import *

class Migration:
    
    def forwards(self, orm):
        db.rename_table('roles', 'pidauth_role')
        db.rename_table('domains', 'pidauth_domain')
    
    
    def backwards(self, orm):
        db.rename_table('pidauth_domain', 'domains')
        db.rename_table('pidauth_role', 'roles')
    
    
    models = {
        'pidauth.role': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'role': ('models.CharField', [], {'max_length': '64'}),
            'updated_at': ('models.DateTimeField', [], {'auto_now': 'True'})
        },
        'pidauth.domain': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255', 'unique': 'True'}),
            'updated_at': ('models.DateTimeField', [], {'auto_now': 'True'})
        }
    }
    
    complete_apps = ['pidauth']
