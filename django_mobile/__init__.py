import threading
from django.core.exceptions import ImproperlyConfigured
from django_mobile.conf import settings

_local = threading.local()


def get_flavour(request=None, default=None):
    
    flavour = None
    request = request or getattr(_local, 'request', None)

    # get flavour from from the session. If the user explicitly requests
    # a specific flavour with a request parameter, the value we get
    # here will be taped over by that.
    if request:
        flavour = request.session.get(settings.FLAVOURS_SESSION_KEY, None);
    
 
    if not flavour and hasattr(request, 'flavour'):
           
        flavour = request.flavour
    # if set out of a request-response cycle its stored on the thread local
    if not flavour:
        flavour = getattr(_local, 'flavour', default)
    # if something went wrong we return the very default flavour
    if flavour not in settings.FLAVOURS:
        flavour = settings.FLAVOURS[0]
    return flavour


def set_flavour(flavour, request=None, permanent=False):

    if flavour not in settings.FLAVOURS:
        raise ValueError(
            u"'%r' is no valid flavour. Allowed flavours are: %s" % (
                flavour,
                ', '.join(settings.FLAVOURS),))
    request = request or getattr(_local, 'request', None)
    if request:
        request.flavour = flavour
        if permanent:
            request.session[settings.FLAVOURS_SESSION_KEY] = flavour

    elif permanent:
        raise ValueError(
            u'Cannot set flavour permanently, no request available.')
    _local.flavour = flavour


def _set_request_header(request, flavour):
    request.META['HTTP_X_FLAVOUR'] = flavour


def _init_flavour(request):
    global _local
    _local = threading.local()
    _local.request = request
    if hasattr(request, 'flavour'):
        _local.flavour = request.flavour
    if not hasattr(_local, 'flavour'):
        _local.flavour = settings.FLAVOURS[0]
