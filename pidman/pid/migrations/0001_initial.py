
from south.db import db
from django.db import models
from pidman.pid.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Pid'
        db.create_table('pid_pid', (
            ('id', orm['pid.Pid:id']),
            ('pid', orm['pid.Pid:pid']),
            ('domain', orm['pid.Pid:domain']),
            ('name', orm['pid.Pid:name']),
            ('ext_system', orm['pid.Pid:ext_system']),
            ('ext_system_key', orm['pid.Pid:ext_system_key']),
            ('creator', orm['pid.Pid:creator']),
            ('created_at', orm['pid.Pid:created_at']),
            ('editor', orm['pid.Pid:editor']),
            ('type', orm['pid.Pid:type']),
            ('updated_at', orm['pid.Pid:updated_at']),
            ('policy', orm['pid.Pid:policy']),
        ))
        db.send_create_signal('pid', ['Pid'])
        
        # Adding model 'ExtSystem'
        db.create_table('pid_extsystem', (
            ('id', orm['pid.ExtSystem:id']),
            ('name', orm['pid.ExtSystem:name']),
            ('key_field', orm['pid.ExtSystem:key_field']),
            ('updated_at', orm['pid.ExtSystem:updated_at']),
        ))
        db.send_create_signal('pid', ['ExtSystem'])
        
        # Adding model 'Proxy'
        db.create_table('pid_proxy', (
            ('id', orm['pid.Proxy:id']),
            ('name', orm['pid.Proxy:name']),
            ('transform', orm['pid.Proxy:transform']),
            ('updated_at', orm['pid.Proxy:updated_at']),
        ))
        db.send_create_signal('pid', ['Proxy'])
        
        # Adding model 'Policy'
        db.create_table('pid_policy', (
            ('id', orm['pid.Policy:id']),
            ('created_at', orm['pid.Policy:created_at']),
            ('commitment', orm['pid.Policy:commitment']),
            ('title', orm['pid.Policy:title']),
        ))
        db.send_create_signal('pid', ['Policy'])
        
        # Adding model 'Domain'
        db.create_table('pid_domain', (
            ('id', orm['pid.Domain:id']),
            ('name', orm['pid.Domain:name']),
            ('updated_at', orm['pid.Domain:updated_at']),
            ('policy', orm['pid.Domain:policy']),
            ('parent', orm['pid.Domain:parent']),
        ))
        db.send_create_signal('pid', ['Domain'])
        
        # Adding model 'Target'
        db.create_table('pid_target', (
            ('id', orm['pid.Target:id']),
            ('pid', orm['pid.Target:pid']),
            ('uri', orm['pid.Target:uri']),
            ('qualify', orm['pid.Target:qualify']),
            ('proxy', orm['pid.Target:proxy']),
            ('active', orm['pid.Target:active']),
            ('noid', orm['pid.Target:noid']),
        ))
        db.send_create_signal('pid', ['Target'])
        
        # Creating unique_together for [pid, qualify] on Target.
        db.create_unique('pid_target', ['pid_id', 'qualify'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [pid, qualify] on Target.
        db.delete_unique('pid_target', ['pid_id', 'qualify'])
        
        # Deleting model 'Pid'
        db.delete_table('pid_pid')
        
        # Deleting model 'ExtSystem'
        db.delete_table('pid_extsystem')
        
        # Deleting model 'Proxy'
        db.delete_table('pid_proxy')
        
        # Deleting model 'Policy'
        db.delete_table('pid_policy')
        
        # Deleting model 'Domain'
        db.delete_table('pid_domain')
        
        # Deleting model 'Target'
        db.delete_table('pid_target')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'linkcheck.link': {
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'url': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': "orm['linkcheck.Url']"})
        },
        'linkcheck.url': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_checked': ('django.db.models.fields.DateTimeField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'still_exists': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'pid.domain': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'collections'", 'null': 'True', 'db_column': "'parent_id'", 'to': "orm['pid.Domain']"}),
            'policy': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pid.Policy']", 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'pid.extsystem': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key_field': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '127'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'pid.pid': {
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created'", 'to': "orm['auth.User']"}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pid.Domain']"}),
            'editor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'edited'", 'to': "orm['auth.User']"}),
            'ext_system': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pid.ExtSystem']", 'null': 'True', 'blank': 'True'}),
            'ext_system_key': ('django.db.models.fields.CharField', [], {'max_length': '1023', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1023', 'blank': 'True'}),
            'pid': ('django.db.models.fields.CharField', [], {'default': "u'18zg'", 'unique': 'True', 'max_length': '255'}),
            'policy': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pid.Policy']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'pid.policy': {
            'commitment': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'pid.proxy': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '127'}),
            'transform': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'pid.target': {
            'Meta': {'unique_together': "(('pid', 'qualify'),)"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'linkcheck_link': ('django.contrib.contenttypes.generic.GenericRelation', [], {'to': "orm['linkcheck.Link']"}),
            'noid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'editable': 'False'}),
            'pid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pid.Pid']"}),
            'proxy': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pid.Proxy']", 'null': 'True', 'blank': 'True'}),
            'qualify': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '2048'})
        }
    }
    
    complete_apps = ['pid']
