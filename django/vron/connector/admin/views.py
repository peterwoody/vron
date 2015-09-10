##########################
# Imports
##########################
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.forms.models import inlineformset_factory
from django.db import transaction
from django.db.models import ProtectedError
from vron.core.util import build_datatable_json
from vron.core.decorators import restrict_internal_ips
from vron.admin.views import admin_check





#######################
# AVAILABILITY VIEWS
#######################
@restrict_internal_ips
#@permission_required( 'core.admin_view_immigration_rule', login_url = 'admin:login' )
@user_passes_test( admin_check )
def list_availability_requests( request ):
    """
    Lists all availability API requests

    :param: request
    :return: String
    """
    return HttpResponse( 'list_availability_requests')
    """
    context = {}
    return render( request, 'points/admin/question/list.html', context )
    """





#######################
# BOOKING VIEWS
#######################
@restrict_internal_ips
#@permission_required( 'core.admin_view_immigration_rule', login_url = 'admin:login' )
@user_passes_test( admin_check )
def list_booking_requests( request ):
    """
    Lists all booking API requests

    :param: request
    :return: String
    """
    return HttpResponse( 'list_booking_requests')
    """
    context = {}
    return render( request, 'points/admin/question/list.html', context )
    """