from django.http import HttpResponse


class HttpResponseUnauthorized(HttpResponse):
    '''Variant of Django's :class:`django.http.HttpResponse` for status code
    401 'Unauthorized'.  Takes a single required argument of expected
    authentication method (currently only supports one) to populate the
    WWW-Authenticate header that is required in a 401 response.  Example use::

        HttpResponseUnauthorized('my realm')

    '''
    status_code = 401

    def __init__(self, realm='Restricted Access'):
        HttpResponse.__init__(self)
        self['WWW-Authenticate'] = 'Basic realm="%s"' % realm