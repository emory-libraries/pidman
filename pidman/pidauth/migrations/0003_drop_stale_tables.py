
from south.db import db
from django.db import models
from pidman.pidauth.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Deleting model 'permission'
        db.delete_table(u'permissions')
        
        # Deleting model 'user'
        db.delete_table(u'users')
    
    
    def backwards(self, orm):
        
        # Adding model 'user'
        db.create_table(u'users', (
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('is_superuser', models.BooleanField()),
            ('last', models.CharField(max_length=127)),
            ('id', models.AutoField(primary_key=True)),
            ('username', models.CharField(unique=True, max_length=32)),
            ('password', models.CharField(max_length=150)),
            ('email', models.EmailField(unique=True, max_length=320)),
            ('first', models.CharField(max_length=127)),
        ))
        db.send_create_signal('pidauth', ['user'])
        
        # Adding model 'permission'
        db.create_table(u'permissions', (
            ('domain', models.ForeignKey(orm.domain)),
            ('role', models.ForeignKey(orm.role)),
            ('id', models.AutoField(primary_key=True)),
            ('user', models.ForeignKey(orm.user)),
        ))
        db.send_create_signal('pidauth', ['permission'])
        
    
    
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
            '_stub': True,
            'id': 'models.AutoField(primary_key=True)'
        }
    }
    
    complete_apps = ['pidauth']
