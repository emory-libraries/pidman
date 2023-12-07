from functools import wraps
import base64
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser

def basic_authentication(view_method):
    '''This decorator performs Basic Authentication when an HTTP_AUTHORIZATION
    header is set in the request.  If no credentials are present or authentication
    fails, the user on the request object passed to the view method will be an
    instance of Django's :class:`django.contrib.auth.models.AnonymousUser`.

    Intended for views that are accessed programmatically.
    '''
    # based in part on http://djangosnippets.org/snippets/243/
    # also based on authentication example from p. 361 of _RESTful Web Services_ 
    @wraps(view_method)
    def view_decorator(request, *args, **kwargs):
        auth_info = request.META.get('HTTP_AUTHORIZATION', None)
        basic = 'Basic '
        if auth_info and auth_info.startswith(basic):
            basic_info = auth_info[len(basic):]
            u, p = base64.b64decode(basic_info.encode('ascii')).decode('ascii').split(':')
            request.user = authenticate(username=u, password=p)
        else:
            request.user = None

        # if authentication failed or credentials were not passed, user will be None
        if request.user is None:
            request.user = AnonymousUser()  # convert to django's anonymous user

        return view_method(request, *args, **kwargs)
    return view_decorator