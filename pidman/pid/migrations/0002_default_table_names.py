
from south.db import db
from django.db import models
from pidman.pid.models import *

class Migration:
    
    def forwards(self, orm):
        db.rename_table('ext_systems', 'pid_extsystem')
        db.rename_table('pids', 'pid_pid')
        db.rename_column('pid_pid', 'modified_by', 'editor_id')
        db.rename_table('proxies', 'pid_proxy')
        db.rename_table('targets', 'pid_target')
        db.rename_column('pid_target', 'pid', 'noid')
    
    
    def backwards(self, orm):
        db.rename_column('pid_target', 'noid', 'pid')
        db.rename_table('pid_target', 'targets')
        db.rename_table('pid_proxy', 'proxies')
        db.rename_column('pid_pid', 'editor_id', 'modified_by')
        db.rename_table('pids', 'pid_pid')
        db.rename_table('pid_extsystem', 'ext_systems')
    
    
    models = {
        'pid.pid': {
            'Meta': {'db_table': "u'pids'"},
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
            'Meta': {'db_table': "u'ext_systems'"},
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
            'Meta': {'db_table': "u'proxies'"},
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
            'Meta': {'unique_together': "(('pid','qualify'))", 'db_table': "u'targets'"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'noid': ('MirrorField', ["'pid'", "'pid'"], {'editable': 'False', 'db_column': "'pid'"}),
            'pid': ('models.ForeignKey', ['Pid'], {}),
            'proxy': ('models.ForeignKey', ['Proxy'], {'null': 'True', 'blank': 'True'}),
            'qualify': ('models.CharField', ['"Qualifier"'], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'uri': ('models.CharField', [], {'max_length': '2048'})
        }
    }
    
    complete_apps = ['pid']
