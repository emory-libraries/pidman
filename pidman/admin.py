from django.contrib import auth
from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry
from downtime.models import Period
from eultheme.models import Banner
from logentry_admin.admin import LogEntryAdmin

import sequences


class PidmanAdminSite(AdminSite):
    site_header = 'Persistent Identifier Manager'
    site_title = 'PID Manager Adminstration'
    index_template = 'admin/pidman_index.html'

admin_site = PidmanAdminSite()
# NOTE: admin autodiscover doesn't work with custom admin sites,
# so we have to register here any models we care about
admin_site.register(auth.models.Group, auth.admin.GroupAdmin)
admin_site.register(auth.models.User, auth.admin.UserAdmin)
admin_site.register(sequences.models.Sequence, sequences.admin.Sequence)

# eultheme / downtime
admin_site.register(Period)
admin_site.register(Banner)
admin_site.register(LogEntry, LogEntryAdmin)


def template_settings(request):
    '''Template context processor to add settings for use on any page.'''

    context_extras = {
        'site_title': PidmanAdminSite.site_header
    }
    return context_extras

