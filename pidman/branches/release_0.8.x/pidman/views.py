from django.http import HttpResponseGone, HttpResponsePermanentRedirect, HttpResponseRedirect

# Views needed by the site as a whole but not any particular app.
# Effectively just a placeholder for a redirect for now.

def redirect_to(request, url, permanent=True, **kwargs):
    """
    Redirect to a given URL.

    django.views.generic.simple.redirect_to returns a permanent redirect,
    but we want a temporary. Django trunk has this feature, but 1.0.2
    doesn't. Implement it here until we upgrade to a version that includes
    it.
    """
    if url is None:
        return HttpResponseGone()
    elif permanent:
        return HttpResponsePermanentRedirect(url % kwargs)
    else:
        return HttpResponseRedirect(url % kwargs)
