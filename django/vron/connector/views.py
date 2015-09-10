"""
Admin Views

These are the views that control logic flow for
the templates on admin
"""

##########################
# Imports
##########################
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test





#######################
# AVAILABILITY VIEWS
#######################
def check_availability( request ):
    """
    Checks tour availability

    :param: request
    :return: String
    """

    return HttpResponse( 'test' )