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
from vron.connector.models import Config, Log, LogStatus, Key
from vron.connector.admin.forms import ConfigForm, KeyForm, TestForm
from django.conf import settings
from vron.core.util import get_object_or_false
from django.utils.html import strip_spaces_between_tags
import requests
import re





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
        'fields_to_select': [ 'id', 'name', 'value' ],
        'fields_to_search': [ 'id', 'name', 'value' ],
        'default_order_by': 'id',
        'url_base_name': 'config',
        'namespace': 'admin:connector:'
    }

    # Builds json data and return it to the screen
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

    # Instantiates FORM
    form = ConfigForm( request.POST or None )

    # If form was submitted, it tries to validate and save data
    if form.is_valid():

        # Saves User
        config = form.save()
        messages.success( request, 'Config was successfully added.' )

        # Redirects with success message
        return HttpResponseRedirect( reverse( 'admin:connector:config_details', args = ( config.id, ) ) )

    # Template data
    context = { 'form': form, 'cancel_url': reverse( 'admin:connector:config' ) }

    # Prints Template
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

    # Identifies database record
    config = get_object_or_404( Config, pk = config_id )

    # Template data
    context = { 'config': config }

    # Prints Template
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
    # Identifies database record
    config = get_object_or_404( Config, pk = config_id )

    # Instantiates FORM
    form = ConfigForm( request.POST or None, instance = config )

    # When form is submitted , it tries to validate and save data
    if form.is_valid():
        form.save()
        messages.success( request, 'Config was successfully updated.' )
        return HttpResponseRedirect( reverse( 'admin:connector:config_details', args = ( config_id, ) ) )

    # Template data
    context = { 'form': form, 'cancel_url': reverse( 'admin:connector:config_details', args = ( config_id, ) ) }

    # Prints Template
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
    # Identifies database record
    config = get_object_or_404( Config, pk = config_id )

    # Deletes it
    config.delete()

    # Redirects with success message
    messages.success( request, 'Config was successfully deleted.')
    return HttpResponseRedirect( reverse( 'admin:connector:config' ) )





#######################
# KEY VIEWS
#######################
@restrict_internal_ips
@permission_required( 'connector.admin_view_key', login_url = 'admin:login' )
@user_passes_test( admin_check )
def key_list( request ):
    """
    Lists all keys with pagination, order by, search, etc. using www.datatables.net

    :param: request
    :return: String
    """

    # Template data
    context = {}

    # Prints Template
    return render( request, 'connector/admin/key/list.html', context )


@restrict_internal_ips
@permission_required( 'connector.admin_view_key', login_url = 'admin:login' )
@user_passes_test( admin_check )
def key_list_json( request ):
    """
    Generates JSON for the listing (required for the JS plugin www.datatables.net)

    :param: request
    :return: String
    """

    # Searches DB records
    objects = Key.objects.filter()

    # Gets base key to prepend to all keys
    config = get_object_or_false( Config, pk = settings.ID_CONFIG_BASE_API_KEY )
    base_key = config.value

    # settings
    info = {
        'fields_to_select': [ 'id', 'name' ],
        'fields_to_search': [ 'id', 'name', 'comments' ],
        'default_order_by': 'id',
        'url_base_name': 'key',
        'namespace': 'admin:connector:',
        'prepend': {
            'name': base_key
        }
    }

    # Builds json data and return it to the screen
    json = build_datatable_json( request, objects, info )
    return HttpResponse( json )


@restrict_internal_ips
@permission_required( 'connector.admin_add_key', login_url = 'admin:login' )
@user_passes_test( admin_check )
def key_add( request ):
    """
    Add new CONFIG

    :param: request
    :param: key_id
    :return: String
    """

    # Instantiates FORM
    form = KeyForm( request.POST or None )

    # If form was submitted, it tries to validate and save data
    if form.is_valid():

        # Saves User
        key = form.save()
        messages.success( request, 'Key was successfully added.' )

        # Redirects with success message
        return HttpResponseRedirect( reverse( 'admin:connector:key_details', args = ( key.id, ) ) )

    # Gets base key to prepend to all keys
    config = get_object_or_false( Config, pk = settings.ID_CONFIG_BASE_API_KEY )
    base_key = config.value

    # Template data
    context = {
        'form': form,
        'cancel_url': reverse( 'admin:connector:keys' ),
        'base_key': base_key
    }

    # Printss Template
    return render( request, 'connector/admin/key/add.html', context )


@restrict_internal_ips
@permission_required( 'connector.admin_view_key', login_url = 'admin:login' )
@user_passes_test( admin_check )
def key_details( request, key_id ):
    """
    View CONFIG page

    :param: request
    :param: key_id
    :return: String
    """

    # Identifies database record
    key = get_object_or_404( Key, pk = key_id )

    # Gets base key to prepend to all keys
    config = get_object_or_false( Config, pk = settings.ID_CONFIG_BASE_API_KEY )
    base_key = config.value

    # Template data
    context = { 'key': key, 'base_key': base_key }

    # Prints Template
    return render( request, 'connector/admin/key/details.html', context )


@restrict_internal_ips
@permission_required( 'connector.admin_change_key', login_url = 'admin:login' )
@user_passes_test( admin_check )
def key_edit( request, key_id ):
    """
    Edit CONFIG data

    :param: request
    :param: key_id
    :return: String
    """
    # Identifies database record
    key = get_object_or_404( Key, pk = key_id )

    # Instantiates FORM
    form = KeyForm( request.POST or None, instance = key )

    # When form is submitted , it tries to validate and save data
    if form.is_valid():
        form.save()
        messages.success( request, 'Key was successfully updated.' )
        return HttpResponseRedirect( reverse( 'admin:connector:key_details', args = ( key_id, ) ) )

    # Gets base key to prepend to all keys
    config = get_object_or_false( Config, pk = settings.ID_CONFIG_BASE_API_KEY )
    base_key = config.value

    # Template data
    context = {
        'form': form,
        'cancel_url': reverse( 'admin:connector:key_details', args = ( key_id, ) ),
        'base_key': base_key
    }

    # Prints Template
    return render( request, 'connector/admin/key/edit.html', context )


@restrict_internal_ips
@permission_required( 'connector.admin_delete_key', login_url = 'admin:login' )
@user_passes_test( admin_check )
def key_delete( request, key_id ):
    """
    Delete CONFIG action.

    :param: request
    :param: key_id
    :return: String
    """
    # Identifies database record
    key = get_object_or_404( Key, pk = key_id )

    # Deletes it
    key.delete()

    # Redirects with success message
    messages.success( request, 'Key was successfully deleted.')
    return HttpResponseRedirect( reverse( 'admin:connector:keys' ) )





#######################
# TEST VIEWS
#######################
@restrict_internal_ips
@user_passes_test( admin_check )
def test( request ):
    """
    Test API request

    :param: request
    :return: String
    """

    # Instantiates FORM
    response = ''
    form = TestForm( request.POST or None )

    # If form was submitted, it tries to submit to API url
    if form.is_valid():

        # Removes empty spaces between tags
        xml = strip_spaces_between_tags( request.POST['xml'] )
        xml = re.sub( r'^\s+<','<', xml )

        # sends post request to the API url
        headers = { 'Content-Type': 'application/xml' }
        response = requests.post(
            settings.BASE_URL + reverse( 'connector:api' ) ,
            data = xml,
            headers = headers
        ).text

    # Template data
    context = { 'form': form, 'cancel_url': reverse( 'admin:home' ), 'response': response }

    # Prints Template
    return render( request, 'connector/admin/test/add.html', context )