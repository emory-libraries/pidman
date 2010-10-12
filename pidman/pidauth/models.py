from django.db import models

class Role(models.Model):
    role = models.CharField(max_length=64)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.role

    
class Domain(models.Model):
    name = models.CharField(unique=True, max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name
