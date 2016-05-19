from django.contrib import admin
from django import forms
from django.forms.models import ModelForm, ModelChoiceField
from django.forms import ValidationError

from mptt.admin import MPTTModelAdmin, MPTTAdminForm
from mptt.fields import TreeNodeChoiceField

from pidman.admin import admin_site
from pidman.pid.ark_utils import normalize_ark, invalid_qualifier_characters
from pidman.pid.models import ExtSystem, Pid, Proxy, Target, Policy, Domain


class TargetInlineForm(ModelForm):
    """Base Target inline form for use in editing ARKs and PURLs."""
    class Meta:
        model = Target
        fields = ('qualify', 'uri', 'proxy', 'active')

    def clean_qualify(self):
        # check for any characters not allowed in the qualifier
        invalid_chars = invalid_qualifier_characters(self.cleaned_data["qualify"])
        if invalid_chars:
            raise ValidationError("Not permitted: " + ', '.join(invalid_chars))
        # normalize according to how the ARK will be resolved
        return normalize_ark(self.cleaned_data["qualify"])

class TargetInline(admin.TabularInline):
    model = Target
    fields = ('qualify', 'uri', 'proxy', 'active')
    # no max, default number of extra fields
    form = TargetInlineForm
    can_delete = True      # allow ARK target deletion (e.g., qualifiers)

# NOTE: should be possible to extend inline template here
# to display link status - last checked / message / etc

class PurlTargetInline(TargetInline):
    verbose_name_plural = "Target"
    max_num = 1
    can_delete = False      # do not allow PURL target deletion (only one target)
    fields = ('uri', 'proxy', 'active')

class PidAdminForm(ModelForm):
    domain = TreeNodeChoiceField(queryset=Domain.objects.all())
    class Meta:
        model = Pid
        exclude = []

class PidAdmin(admin.ModelAdmin):
    # browse display: type (ark/purl), domain/collection, name/description, and pid url (not target url)
    # note: including pid for link to edit page, since name is optional and not always present
    # including dates in list display for sorting purposes
    # sort columns by: type, domain/collection, name, (pid url?), date created/modified ascending/descending

    ####### removing domain fixed the problem need to find query for domain
    list_display = ('pid', 'truncated_name', 'type', 'created_at', 'updated_at',
                    'domain', "primary_target_uri", "is_active", 'linkcheck_status')

    # filters: collection/domain, creator/user, type (ark/purl), date ranges (created or modified)
    list_filter = (
        'type', ('domain', admin.RelatedOnlyFieldListFilter),
        'ext_system',
        ('creator', admin.RelatedOnlyFieldListFilter),
        'created_at', 'updated_at')
    list_select_related = True  # may want to limit this some
    form = PidAdminForm

    # now possible in django 1.1 - fields to use here?
    # list_editable = ('name', 'domain')
    date_hierarchy = 'created_at'
    search_fields = ['name', 'pid', 'ext_system_key', 'target__uri']
    # keep pid type in a separate fieldset in order to suppress it on edit
    fieldset_pidtype = ('Pid Type', {
            'fields': ('type',),
            'description': "Select type of pid to create."
    })
    fieldset_pidinfo = ("Pid Information", {
            'fields': ('name', 'domain', ('ext_system', 'ext_system_key'), 'policy')
    })
    fieldsets = (fieldset_pidtype, fieldset_pidinfo)

    # by default, use purl target inline; if saved as an ark, will use TargetInline
    inlines = [PurlTargetInline]

    class Media:
        css = {
            "all": ("css/font-awesome.min.css",)
        }

    def get_inline_instances(self, request, obj=None):
        # get target inline class based on the object
        # when adding a new object, restrict targets to purl type until saved
        # once the object is saved, display purl or ark target inline
        # edit form based on pid type
        inlines = list(self.inlines)  # make a new copy of inline config
        if obj is not None and obj.type == 'Ark':
            inlines[0] = TargetInline

        return [inline(self.model, self.admin_site) for inline in inlines]

    # set creator and editor to current user before saving
    def save_model(self, request, obj, form, change):
        obj.editor = request.user
        if not (change):
            obj.creator = request.user
        obj.save()

    # disallow delete of Pids set targets to inactive instead
    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        # extend queryset to prefetch targets & linkcheck status,
        # which are used in the change list display
        pidqs = super(PidAdmin, self).get_queryset(request)
        pidqs = pidqs.prefetch_related('target_set', 'target_set__linkcheck__url')
        return pidqs


class ExtSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_field', 'updated_at')

class ProxyAdmin(admin.ModelAdmin):
    list_display = ('name', 'transform', 'updated_at')

class PolicyAdmin(admin.ModelAdmin):
    list_display = ('commitment', 'created_at')

# class DomainAdminForm(forms.ModelForm):
class DomainAdminForm(MPTTAdminForm):
    # restrict list of domains allowed to be parents to those domains
    # without a parent (1 level deep only)
    parent = TreeNodeChoiceField(queryset=Domain.objects.filter(parent__isnull=True),
        required=False)
    class Meta:
        model = Domain
        exclude = []

    def clean_parent(self):
        parent = self.cleaned_data["parent"]
        if parent:
            # check parent id - cannot point to self
            if parent.id == self.instance.id:
                raise ValidationError("Not permitted: a domain can not be its own parent",
                   code='invalid')
            # restrict hierarchy to one level
            elif parent.parent:
                raise ValidationError("Domain hierarchy restricted to depth of 1; " +
                                parent.name + " is a collection of " + parent.parent.name,
                                code='invalid')
        return parent


    def clean(self):
        # policy is optional by default, but top-level domains must have one (can't inherit from parent)
        if not self.cleaned_data.get('parent', None) and not self.cleaned_data['policy']:
           raise ValidationError("Policy is required for top-level domains")
        return self.cleaned_data

class CollectionInline(admin.TabularInline):
    model = Domain
    verbose_name = "Domain"
    verbose_name_plural = "Collections"
    # parent = TreeNodeChoiceField(queryset=Domain.objects.all(),
        # level_indicator=u'+--')

class DomainAdmin(MPTTModelAdmin):
    form = DomainAdminForm
    mptt_level_indent = 20

    list_display = ('name', 'num_pids', 'subdomain_count', 'show_policy')
    inlines = [CollectionInline]


admin_site.register(Pid, PidAdmin)
admin_site.register(Proxy, ProxyAdmin)
admin_site.register(ExtSystem, ExtSystemAdmin)
admin_site.register(Policy, PolicyAdmin)
admin_site.register(Domain, DomainAdmin)
