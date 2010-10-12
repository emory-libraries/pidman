
from south.db import db
from django.db import models
from pidman.pid.models import *

class Migration:

    no_dry_run = True

    def forwards(self, orm):
        "Convert all blank qualifiers from null to empty string"
        for target in orm.Target.objects.filter(qualify__isnull=True):
           target.qualify = ''
           target.save()

    
    def backwards(self, orm):
        "Convert all blank qualifiers from empty string to null"
        for target in orm.Target.objects.filter(qualify__exact=''):
           target.qualify = None
           target.save()

    
    models = {
        'pid.pid': {
            'active': ('models.BooleanField', [], {'default': 'True'}),
            'created_at': ('models.DateTimeField', ['"Date Created"'], {'auto_now_add': 'True'}),
            'creator': ('models.ForeignKey', ['User'], {'related_name': "'created'"}),
            'domain': ('models.ForeignKey', ['Domain'], {}),
            'editor': ('models.ForeignKey', ['User'], {'related_name': '"edited"'}),
            'ext_system': ('models.ForeignKey', ['ExtSystem'], {'null': 'True', 'verbose_name': "'External system'", 'blank': 'True'}),
            'ext_system_key': ('models.CharField', ["'External system key'"], {'max_length': '1023', 'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '1023'}),
            'pid': ('models.CharField', [], {'default': 'mint_noid', 'max_length': '255', 'unique': 'True', 'editable': 'False'}),
            'type': ('models.CharField', [], {'max_length': '25'}),
            'updated_at': ('models.DateTimeField', ['"Date Updated"'], {'auto_now': 'True'})
        },
        'pid.extsystem': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'key_field': ('models.CharField', [], {'max_length': '127'}),
            'name': ('models.CharField', [], {'max_length': '127', 'unique': 'True'}),
            'updated_at': ('models.DateTimeField', [], {'auto_now': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'pid.proxy': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '127', 'unique': 'True'}),
            'transform': ('models.CharField', [], {'max_length': '127'}),
            'updated_at': ('models.DateTimeField', [], {'auto_now': 'True'})
        },
        'pidauth.domain': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'pid.target': {
            'Meta': {'unique_together': "(('pid','qualify'))"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'noid': ('MirrorField', ["'pid'", "'pid'"], {'editable': 'False'}),
            'pid': ('models.ForeignKey', ['Pid'], {}),
            'proxy': ('models.ForeignKey', ['Proxy'], {'null': 'True', 'blank': 'True'}),
            'qualify': ('models.CharField', ['"Qualifier"'], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'uri': ('models.CharField', [], {'max_length': '2048'})
        }
    }
    
    complete_apps = ['pid']
