from django.contrib.admin import AdminSite
from django.contrib import auth
import sequences

class PidmanAdminSite(AdminSite):
    site_header = 'Persistent Identifier Manager'
    site_title = 'PID Manager Adminstration'

admin_site = PidmanAdminSite()
# NOTE: admin autodiscover doesn't work with custom admin sites,
# so we have to register here any models we care about
admin_site.register(auth.models.Group, auth.admin.GroupAdmin)
admin_site.register(auth.models.User, auth.admin.UserAdmin)
admin_site.register(sequences.models.Sequence, sequences.admin.Sequence)