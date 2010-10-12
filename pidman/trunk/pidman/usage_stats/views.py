import csv
from django.http import HttpResponse, HttpResponseRedirect
from pidman.usage_stats.models import TargetAccessLog, get_by_fiscal_year
from django.shortcuts import render_to_response

def export(request, year=None):
    #if not authenticated kick to admin to require login
    if not (request.user.is_authenticated() and request.user.is_staff):
        return HttpResponseRedirect('/admin')

    # Create the HttpResponse object with the appropriate CSV header.
    if year:
        y = year
    else:
        y = 'all'

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=usage_log%s.csv' % ('_' + y, )

    writer = csv.writer(response)
    writer.writerow(['NOID', 'Qualifier', 'Public URL', 'Target URL', 'ip', 'timestamp', 'Referring Host', 'User Agent'])

    if year:
        access_log = get_by_fiscal_year(year)
    else:
        access_log = TargetAccessLog.objects.all()

    for usage in access_log:
        writer.writerow([usage.target.noid, usage.target.qualify, usage.target.get_resolvable_url(),
            usage.target.uri, usage.ip, usage.timestamp.strftime("%Y/%m/%d %H:%M:%S"),
            usage.referrer, usage.browser
        ])

    return response
