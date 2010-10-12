from pidman.pid.models import ExtSystem, Pid, Proxy, Target
from django.contrib import admin
from django.forms.models import inlineformset_factory

class TargetInline(admin.TabularInline):
    model = Target
    fields = ('qualify', 'uri', 'proxy')
    # no max, default number of extra fields

class PurlTargetInline(TargetInline):
    verbose_name_plural  = "Target"
    max_num = 1
    fields = ('uri', 'proxy')         
        
class PidAdmin(admin.ModelAdmin):
    list_display = ('pid', 'name', 'type', 'created_at', 'updated_at', "domain", "primary_target_uri")
    list_filter = ['type', 'domain', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    search_fields = ['name', 'pid', 'ext_system_key']
    # keep pid type in a separate fieldset in order to suppress it on edit
    fieldset_pidtype = ('Pid Type', {
            'fields': ('type',),
            'description': "Select type of pid to create."
    })
    fieldset_pidinfo = ("Pid Information", {
            'fields': ('name', 'domain', ('ext_system', 'ext_system_key'), 'active')
    })
    fieldsets = (fieldset_pidtype, fieldset_pidinfo)

    # by default, use purl target inline; if saved as an ark, will use TargetInline
    inlines = [PurlTargetInline]

    # when adding a new object, restrict targets to purl type until saved and type is set
    def add_view(self, request, form_url='', extra_context=None):
        self.inline_instances[0] = PurlTargetInline(self.model, self.admin_site)
        self.fieldsets = (self.fieldset_pidtype, self.fieldset_pidinfo)
        return super(PidAdmin, self).add_view(request, form_url, extra_context)

    # overriding change_view to set target inline based on pid type,
    # and to disallow changing pid type
    def change_view(self, request, object_id, extra_context=None):
        # fieldset is pidinfo only (not allowing users to edit pid type after pid creation)
        self.fieldsets = (self.fieldset_pidinfo,)

        try:
            obj = Pid.objects.get(pk=object_id)
            if (obj.type == "Ark"):
                # for Arks, use default target inline (no max, edit qualifiers)
                self.inline_instances[0] = TargetInline(self.model, self.admin_site)            
            if (obj.type == "Purl"):
                # customized target inline for purls (max =1, no qualifiers)
                self.inline_instances[0] = PurlTargetInline(self.model, self.admin_site)
        except Exception:
            pass        
            
        return super(PidAdmin, self).change_view(request, object_id, extra_context)

    # set creator and editor to current user before saving
    def save_model(self, request, obj, form, change):                
        obj.editor = request.user
        if not (change):
            obj.creator = request.user
        obj.save()

class ExtSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_field', 'updated_at')

class ProxyAdmin(admin.ModelAdmin):
    list_display = ('name', 'transform', 'updated_at')

admin.site.register(Pid, PidAdmin)
admin.site.register(Proxy, ProxyAdmin)
admin.site.register(ExtSystem, ExtSystemAdmin)
