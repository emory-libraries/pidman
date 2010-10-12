
from south.db import db
from django.db import models
from pidman.usage_stats.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'TargetAccessLog'
        db.create_table('usage_stats_targetaccesslog', (
            ('id', orm['usage_stats.TargetAccessLog:id']),
            ('target', orm['usage_stats.TargetAccessLog:target']),
            ('ip', orm['usage_stats.TargetAccessLog:ip']),
            ('timestamp', orm['usage_stats.TargetAccessLog:timestamp']),
            ('referrer', orm['usage_stats.TargetAccessLog:referrer']),
            ('browser', orm['usage_stats.TargetAccessLog:browser']),
        ))
        db.send_create_signal('usage_stats', ['TargetAccessLog'])
        
        # Creating unique_together for [timestamp, ip] on TargetAccessLog.
        db.create_unique('usage_stats_targetaccesslog', ['timestamp', 'ip'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [timestamp, ip] on TargetAccessLog.
        db.delete_unique('usage_stats_targetaccesslog', ['timestamp', 'ip'])
        
        # Deleting model 'TargetAccessLog'
        db.delete_table('usage_stats_targetaccesslog')
        
    
    
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
            'pid': ('django.db.models.fields.CharField', [], {'default': "u'18qr'", 'unique': 'True', 'max_length': '255'}),
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
        },
        'usage_stats.targetaccesslog': {
            'Meta': {'unique_together': "(('timestamp', 'ip'),)"},
            'browser': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'referrer': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pid.Target']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        }
    }
    
    complete_apps = ['usage_stats']
