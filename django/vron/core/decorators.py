"""
Custom decorators to be used by views (https://docs.djangoproject.com/en/1.7/topics/http/decorators/)

You can create own functionalities that will be used before a function is processed.

E.g. create a function "require_http_methods" to use like that on your views:

@require_http_methods(["GET", "POST"])
def my_view(request):
    # I can assume now that only GET or POST requests make it this far
    # ...
    pass

"""

##########################
# Imports
##########################
from functools import wraps
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import available_attrs





##########################
# Function definitions
##########################
def restrict_internal_ips( view_func ):
    """
    A view decorator which returns the provided view function,
    modified to return a 403 when the remote address is not in
    the list of internal IPs defined in settings.
    """

    @wraps( view_func, assigned = available_attrs( view_func ) )
    def _wrapped_view( request, *args, **kwargs ):

        # Pre-process the IP address
        x_forwarded_for = request.META.get( 'HTTP_X_FORWARDED_FOR' )
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get( 'REMOTE_ADDR' )
        
        # If current IP is not in the internal ips list and I am on the
        # production server, redirects the user to the home.
        if ip not in settings.INTERNAL_IPS and settings.IS_PROD == True:
            return HttpResponseRedirect( reverse( 'site:home' ) )
        return view_func( request, *args, **kwargs )

    return _wrapped_view


def secure_required( view_func ):
    """Decorator that makes sure URL is accessed over https."""
    def _wrapped_view_func( request, *args, **kwargs ):
        if not request.is_secure():
            if getattr(settings, 'HTTPS_SUPPORT', True):
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(secure_url)
        return view_func( request, *args, **kwargs )
    return _wrapped_view_func


def ajax_login_required( view_func ):
    """
    Wraps an ajax request and returns HTTP401 if the user is not authenticated.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponse( status = 401 )
    return _wrapped_view


def subscription_required( view_func ):
    """
    Wraps an check to see if there's an active subscription in the session
    """
    def _wrapped_view(request, *args, **kwargs):
        if 'subscription' not in request.session or request.session['subscription'] is None:
            return HttpResponseRedirect( reverse( 'marketplace:immi_box' ) )
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view