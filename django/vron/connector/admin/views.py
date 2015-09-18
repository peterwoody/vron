##########################
# Imports
##########################
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, user_passes_test
from vron.core.util import build_datatable_json
from vron.core.decorators import restrict_internal_ips
from vron.admin.views import admin_check
from vron.connector.models import Config, Log, LogStatus
from vron.connector.admin.forms import ConfigForm





#######################
# CONFIG VIEWS
#######################
@restrict_internal_ips
@permission_required( 'connector.admin_view_config', login_url = 'admin:login' )
@user_passes_test( admin_check )
def config_list( request ):
    """
    Lists all configs with pagination, order by, search, etc. using www.datatables.net

    :param: request
    :return: String
    """

    context = {}
    return render( request, 'connector/admin/config/list.html', context )


@restrict_internal_ips
@permission_required( 'connector.admin_view_config', login_url = 'admin:login' )
@user_passes_test( admin_check )
def config_list_json( request ):
    """
    Generates JSON for the listing (required for the JS plugin www.datatables.net)

    :param: request
    :return: String
    """

    # Query data
    objects = Config.objects.filter()

    # settings
    info = {
        'fields_to_select': [ 'id', 'option_name', 'option_value' ],
        'fields_to_search': [ 'id', 'option_name', 'option_value' ],
        'default_order_by': 'id',
        'url_base_name': 'config',
        'namespace': 'admin:connector:'
    }

    #build json data and return it to the screen
    json = build_datatable_json( request, objects, info )
    return HttpResponse( json )


@restrict_internal_ips
@permission_required( 'connector.admin_add_config', login_url = 'admin:login' )
@user_passes_test( admin_check )
def config_add( request ):
    """
    Add new CONFIG

    :param: request
    :param: config_id
    :return: String
    """

    # Instantiate FORM
    form = ConfigForm( request.POST or None )

    # If form was submitted, it tries to validate and save data
    if form.is_valid():

        # Saves User
        config = form.save()
        messages.success( request, 'Config was successfully added.' )

        # Redirect with success message
        return HttpResponseRedirect( reverse( 'admin:connector:config_details', args = ( config.id, ) ) )

    # Template data
    context = { 'form': form, 'cancel_url': reverse( 'admin:connector:config' ) }

    # Print Template
    return render( request, 'connector/admin/config/add.html', context )


@restrict_internal_ips
@permission_required( 'connector.admin_view_config', login_url = 'admin:login' )
@user_passes_test( admin_check )
def config_details( request, config_id ):
    """
    View CONFIG page

    :param: request
    :param: config_id
    :return: String
    """

    # Identify database record
    config = get_object_or_404( Config, pk = config_id )

    # Template data
    context = { 'config': config }

    # Print Template
    return render( request, 'connector/admin/config/details.html', context )


@restrict_internal_ips
@permission_required( 'connector.admin_change_config', login_url = 'admin:login' )
@user_passes_test( admin_check )
def config_edit( request, config_id ):
    """
    Edit CONFIG data

    :param: request
    :param: config_id
    :return: String
    """
    # Identify database record
    config = get_object_or_404( Config, pk = config_id )

    # Instantiate FORM
    form = ConfigForm( request.POST or None, instance = config )

    # When form is submitted , it tries to validate and save data
    if form.is_valid():
        form.save()
        messages.success( request, 'Config was successfully updated.' )
        return HttpResponseRedirect( reverse( 'admin:connector:config_details', args = ( config_id, ) ) )

    # Template data
    context = { 'form': form, 'cancel_url': reverse( 'admin:connector:config_details', args = ( config_id, ) ) }

    # Print Template
    return render( request, 'connector/admin/config/edit.html', context )


@restrict_internal_ips
@permission_required( 'connector.admin_delete_config', login_url = 'admin:login' )
@user_passes_test( admin_check )
def config_delete( request, config_id ):
    """
    Delete CONFIG action.

    :param: request
    :param: config_id
    :return: String
    """
    # Identify database record
    config = get_object_or_404( Config, pk = config_id )

    # mark as INACTIVE
    config.is_active = False
    config.save()

    # Redirect with success message
    messages.success( request, 'Config was successfully deleted.')
    return HttpResponseRedirect( reverse( 'admin:core:configs' ) )