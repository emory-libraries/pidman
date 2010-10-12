
from south.db import db
from django.db import models
from pidman.pid.models import *

class Migration:

    def forwards(self, orm):
        
        # Adding model 'Target'
        db.create_table(u'targets', (
            ('pid', models.ForeignKey(orm.Pid)),
            ('noid', MirrorField('pid', 'pid', editable=False, db_column='pid')),
            ('uri', models.CharField(max_length=2048)),
            ('qualify', models.CharField("Qualifier", default='', max_length=255, null=True, blank=True)),
            ('proxy', models.ForeignKey(orm.Proxy, null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('pid', ['Target'])
        
        # Adding model 'Proxy'
        db.create_table(u'proxies', (
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('transform', models.CharField(max_length=127)),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(max_length=127, unique=True)),
        ))
        db.send_create_signal('pid', ['Proxy'])
        
        # Adding model 'Pid'
        db.create_table(u'pids', (
            ('domain', models.ForeignKey(orm['pidauth.Domain'])),
            ('name', models.CharField(max_length=1023)),
            ('creator', models.ForeignKey(orm['auth.User'], related_name='created')),
            ('created_at', models.DateTimeField("Date Created", auto_now_add=True)),
            ('pid', models.CharField(default=mint_noid, max_length=255, unique=True, editable=False)),
            ('updated_at', models.DateTimeField("Date Updated", auto_now=True)),
            ('ext_system_key', models.CharField('External system key', max_length=1023, null=True, blank=True)),
            ('ext_system', models.ForeignKey(orm.ExtSystem, null=True, verbose_name='External system', blank=True)),
            ('active', models.BooleanField(default=True)),
            ('type', models.CharField(max_length=25)),
            ('id', models.AutoField(primary_key=True)),
            ('editor', models.ForeignKey(orm['auth.User'], related_name="edited", db_column="modified_by")),
        ))
        db.send_create_signal('pid', ['Pid'])
        
        # Adding model 'ExtSystem'
        db.create_table(u'ext_systems', (
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('key_field', models.CharField(max_length=127)),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(max_length=127, unique=True)),
        ))
        db.send_create_signal('pid', ['ExtSystem'])
        
        # Creating unique_together for [pid, qualify] on Target.
        db.create_unique(u'targets', ['pid_id', 'qualify'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Target'
        db.delete_table(u'targets')
        
        # Deleting model 'Proxy'
        db.delete_table(u'proxies')
        
        # Deleting model 'Pid'
        db.delete_table(u'pids')
        
        # Deleting model 'ExtSystem'
        db.delete_table(u'ext_systems')
        
        # Deleting unique_together for [pid, qualify] on Target.
        db.delete_unique(u'targets', ['pid_id', 'qualify'])
        
    
    
    models = {
        'pid.pid': {
            'Meta': {'db_table': "u'pids'"},
            'active': ('models.BooleanField', [], {'default': 'True'}),
            'created_at': ('models.DateTimeField', ['"Date Created"'], {'auto_now_add': 'True'}),
            'creator': ('models.ForeignKey', ['User'], {'related_name': "'created'"}),
            'domain': ('models.ForeignKey', ['Domain'], {}),
            'editor': ('models.ForeignKey', ['User'], {'related_name': '"edited"', 'db_column': '"modified_by"'}),
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
            'Meta': {'db_table': "u'domains'"},
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
