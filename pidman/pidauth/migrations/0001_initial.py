
from south.db import db
from django.db import models
from pidman.pidauth.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Role'
        db.create_table(u'roles', (
            ('role', models.CharField(max_length=64)),
            ('id', models.AutoField(primary_key=True)),
            ('updated_at', models.DateTimeField(auto_now=True)),
        ))
        db.send_create_signal('pidauth', ['Role'])
        
        # Adding model 'Domain'
        db.create_table(u'domains', (
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(max_length=255, unique=True)),
        ))
        db.send_create_signal('pidauth', ['Domain'])
        
        # Adding model 'User'
        db.create_table(u'users', (
            ('username', models.CharField(max_length=32, unique=True)),
            ('last', models.CharField(max_length=127)),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('id', models.AutoField(primary_key=True)),
            ('is_superuser', models.BooleanField()),
            ('password', models.CharField(max_length=150)),
            ('email', models.EmailField(max_length=320, unique=True)),
            ('first', models.CharField(max_length=127)),
        ))
        db.send_create_signal('pidauth', ['User'])
        
        # Adding model 'Permission'
        db.create_table(u'permissions', (
            ('domain', models.ForeignKey(orm.Domain)),
            ('role', models.ForeignKey(orm.Role)),
            ('id', models.AutoField(primary_key=True)),
            ('user', models.ForeignKey(orm.User)),
        ))
        db.send_create_signal('pidauth', ['Permission'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Role'
        db.delete_table(u'roles')
        
        # Deleting model 'Domain'
        db.delete_table(u'domains')
        
        # Deleting model 'User'
        db.delete_table(u'users')
        
        # Deleting model 'Permission'
        db.delete_table(u'permissions')
        
    
    
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
