from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from pidman.pid.models import Target, Pid
from pidman.pid.ark_utils import normalize_ark

def resolve_purl(request, noid):
    return resolve_pid(noid)

def resolve_ark(request, naan, noid, qual=''):
    noid = normalize_ark(noid)
    if qual:
        qual = normalize_ark(qual)

    full_path = request.get_full_path()
    # if last letter is ? then metadata or preservation commitment should be displayed
    # NOTE: REQUEST_URI is *ONLY* available when running under mod_wsgi,
    # and full path only includes ? if there is a query string. 
    # See README file for more details.
    if qual == '' and full_path[-1] == "?" or ('REQUEST_URI' in request.META.keys()
        and request.META['REQUEST_URI'][-1] == "?"):
        return ark_metadata(request, noid)
    return resolve_pid(noid, qual)

def resolve_pid(noid, qual=''):
    t = get_object_or_404(Target, noid__exact=noid, qualify=qual, active=True)
    url = t.uri
    if (t.proxy):
        url = t.proxy.transform + url
    return HttpResponseRedirect(url)

# ARK spec 5.1.2 generic description service
# ARK spec 5.1.1 generic policy service
def ark_metadata(request, noid):
    pid = get_object_or_404(Pid, pid__exact=noid)
    full_path = request.get_full_path()
    if full_path[-2:] == "??":
        policy = pid.get_policy()
    else:
        policy = None
        
    return render_to_response("resolver/about",
                              {"pid": pid, "policy" : policy},
                              mimetype="text/plain")


