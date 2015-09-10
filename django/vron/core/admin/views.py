##########################
# Imports
##########################
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from wannamigrate.admin.forms import (
    AdminUserForm, GroupForm, UserForm
)
from wannamigrate.core.models import UserStats
from wannamigrate.points.models import UserResult
from wannamigrate.core.util import build_datatable_json
from wannamigrate.core.mailer import Mailer
from wannamigrate.core.decorators import restrict_internal_ips
from wannamigrate.admin.views import admin_check





#######################
# USERS VIEWS
#######################
@restrict_internal_ips
@permission_required( 'core.admin_view_user', login_url = 'admin:login' )
@user_passes_test( admin_check )
def user_list( request ):
    """
    Lists all users with pagination, order by, search, etc. using www.datatables.net

    :param: request
    :return: String
    """

    context = {}
    return render( request, 'core/admin/user/list.html', context )


@restrict_internal_ips
@permission_required( 'core.admin_view_user', login_url = 'admin:login' )
@user_passes_test( admin_check )
def user_list_json( request ):
    """
    Generates JSON for the listing (required for the JS plugin www.datatables.net)

    :param: request
    :return: String
    """

    # Query data
    user = get_user_model()
    objects = user.objects.filter( is_admin = False, is_superuser = False )

    # settings
    info = {
        'fields_to_select': [ 'id', 'name', 'email' ],
        'fields_to_search': [ 'id', 'name', 'email' ],
        'default_order_by': 'id',
        'url_base_name': 'user',
        'namespace': 'admin:core:'
    }

    #build json data and return it to the screen
    json = build_datatable_json( request, objects, info )
    return HttpResponse( json )


@restrict_internal_ips
@permission_required( 'core.admin_add_user', login_url = 'admin:login' )
@user_passes_test( admin_check )
def user_add( request ):
    """
    Add new  USER

    :param: request
    :param: user_id
    :return: String
    """

    # Instantiate FORM
    form = UserForm( request.POST or None )

    # If form was submitted, it tries to validate and save data
    if form.is_valid():

        # Sets additional data
        form.is_active = True
        form.is_admin = False

        # Saves User
        user = form.save()
        messages.success( request, 'User was successfully added.' )

        # Sends Welcome Email to User
        # TODO Change this to a celery/signal background task
        Mailer.send_welcome_email( user )

        # Redirect with success message
        return HttpResponseRedirect( reverse( 'admin:core:user_details', args = ( user.id, ) ) )

    # Template data
    context = { 'form': form, 'cancel_url': reverse( 'admin:core:users' ) }

    # Print Template
    return render( request, 'core/admin/user/add.html', context )


@restrict_internal_ips
@permission_required( 'core.admin_view_user', login_url = 'admin:login' )
@user_passes_test( admin_check )
def user_details( request, user_id ):
    """
    View  USER page

    :param: request
    :param: user_id
    :return: String
    """

    # Identify database record
    user = get_object_or_404( get_user_model(), pk = user_id )

    # Get user results
    try:
        user_result = user.userresult_set.select_related( 'country__name' )
    except UserResult.DoesNotExist:
        user_result = False

    # Get user registrion % (stats)
    try:
        user_stats = UserStats.objects.filter( user = user )
    except UserStats.DoesNotExist:
        user_stats = False

    # Template data
    context = { 'user': user, 'user_result': user_result, 'user_stats': user_stats }

    # Print Template
    return render( request, 'core/admin/user/details.html', context )


@restrict_internal_ips
@permission_required( 'core.admin_view_user', login_url = 'admin:login' )
@user_passes_test( admin_check )
def login_as_user( request, user_id ):
    """
    View  USER page

    :param: request
    :param: user_id
    :return: String
    """

    # Identify database record
    user = get_object_or_404( get_user_model(), pk = user_id )

    # logs out current user
    auth_logout( request )

    # Logs user in
    user = authenticate( email = user.email, id = user.id, password_hash = user.password )
    auth_login( request, user )
    return HttpResponseRedirect( reverse( "site:dashboard" ) )



@restrict_internal_ips
@permission_required( 'core.admin_change_user', login_url = 'admin:login' )
@user_passes_test( admin_check )
def user_edit( request, user_id ):
    """
    Edit  USER personal data

    :param: request
    :param: user_id
    :return: String
    """
    # Identify database record
    user = get_object_or_404( get_user_model(), pk = user_id )

    # Instantiate FORM
    form = UserForm( request.POST or None, instance = user )

    # When form is submitted , it tries to validate and save data
    if form.is_valid():
        form.save()
        messages.success( request, 'User was successfully updated.' )
        return HttpResponseRedirect( reverse( 'admin:core:user_details', args = ( user_id, ) ) )

    # Template data
    context = { 'form': form, 'cancel_url': reverse( 'admin:core:user_details', args = ( user_id, ) ) }

    # Print Template
    return render( request, 'core/admin/user/edit.html', context )


@restrict_internal_ips
@permission_required( 'core.admin_delete_user', login_url = 'admin:login' )
@user_passes_test( admin_check )
def user_delete( request, user_id ):
    """
    Delete  USER action.
    In the case of users, we never delete them, we just put as 'INACTIVE'

    :param: request
    :param: user_id
    :return: String
    """
    # Identify database record
    user = get_object_or_404( get_user_model(), pk = user_id )

    # mark as INACTIVE
    user.is_active = False
    user.save()

    # Redirect with success message
    messages.success( request, 'User was successfully marked as INACTIVE.')
    return HttpResponseRedirect( reverse( 'admin:core:users' ) )





#######################
# ADMIN USERS VIEWS
#######################
@restrict_internal_ips
@permission_required( 'core.admin_view_admin_user', login_url = 'admin:login' )
@user_passes_test( admin_check )
def admin_user_list( request ):
    """
    Lists all admin users with pagination, order by, search, etc. using www.datatables.net

    :param: request
    :return: String
    """

    context = {}
    return render( request, 'core/admin/admin_user/list.html', context )


@restrict_internal_ips
@permission_required( 'core.admin_view_admin_user', login_url = 'admin:login' )
@user_passes_test( admin_check )
def admin_user_list_json( request ):
    """
    Generates JSON for the listing (required for the JS plugin www.datatables.net)

    :param: request
    :return: String
    """

    # Query data
    user = get_user_model()
    objects = user.objects.filter( is_admin = True )

    # settings
    info = {
        'fields_to_select': [ 'id', 'name', 'email', 'is_superuser' ],
        'fields_to_search': [ 'id', 'name', 'email', 'is_superuser' ],
        'default_order_by': 'id',
        'url_base_name': 'admin_user',
        'namespace': 'admin:core:'
    }

    #build json data and return it to the screen
    json = build_datatable_json( request, objects, info )
    return HttpResponse( json )


@restrict_internal_ips
@permission_required( 'core.admin_add_admin_user', login_url = 'admin:login' )
@user_passes_test( admin_check )
def admin_user_add( request ):
    """
    Add new Admin USER

    :param: request
    :param: user_id
    :return: String
    """

    # Instantiate FORM
    form = AdminUserForm( request.POST or None )

    # If form was submitted, it tries to validate and save data
    if form.is_valid():

        # Sets additional data
        form.is_active = True
        form.is_admin = True

        # Saves User
        user = form.save()
        messages.success( request, 'User was successfully added.' )

        # Sends Welcome Email to User
        # TODO Change this to a celery/signal background task
        Mailer.send_welcome_email( user )

        # Redirect with success message
        return HttpResponseRedirect( reverse( 'admin:core:admin_user_details', args = ( user.id, ) ) )

    # Template data
    context = { 'form': form, 'cancel_url': reverse( 'admin:core:admin_users' ) }

    # Print Template
    return render( request, 'core/admin/admin_user/add.html', context )


@restrict_internal_ips
@permission_required( 'core.admin_view_admin_user', login_url = 'admin:login' )
@user_passes_test( admin_check )
def admin_user_details( request, user_id ):
    """
    View Admin USER page

    :param: request
    :param: user_id
    :return: String
    """

    # Identify database record
    user = get_object_or_404( get_user_model(), pk = user_id )

    # Template data
    context = { 'user': user }

    # Print Template
    return render( request, 'core/admin/admin_user/details.html', context )


@restrict_internal_ips
@permission_required( 'core.admin_change_admin_user', login_url = 'admin:login' )
@user_passes_test( admin_check )
def admin_user_edit( request, user_id ):
    """
    Edit Admin USER personal data

    :param: request
    :param: user_id
    :return: String
    """
    # Identify database record
    user = get_object_or_404( get_user_model(), pk = user_id )

    # Instantiate FORM
    form = AdminUserForm( request.POST or None, instance = user )

    # When form is submitted , it tries to validate and save data
    if form.is_valid():
        form.save()
        messages.success( request, 'User was successfully updated.' )
        return HttpResponseRedirect( reverse( 'admin:core:admin_user_details', args = ( user_id, ) ) )

    # Template data
    context = { 'form': form, 'cancel_url': reverse( 'admin:core:admin_user_details', args = ( user_id, ) ) }

    # Print Template
    return render( request, 'core/admin/admin_user/edit.html', context )


@restrict_internal_ips
@permission_required( 'core.admin_delete_admin_user', login_url = 'admin:login' )
@user_passes_test( admin_check )
def admin_user_delete( request, user_id ):
    """
    Delete Admin USER action.
    In the case of users, we never delete them, we just put as 'INACTIVE'

    :param: request
    :param: user_id
    :return: String
    """
    # Identify database record
    user = get_object_or_404( get_user_model(), pk = user_id )

    # mark as INACTIVE
    user.is_active = False
    user.save()

    # Redirect with success message
    messages.success( request, 'User was successfully marked as INACTIVE.')
    return HttpResponseRedirect( reverse( 'admin:core:admin_users' ) )





#######################
# GROUPS AND PERMISSIONS VIEWS
#######################
@restrict_internal_ips
@permission_required( 'auth.view_group', login_url = 'admin:login' )
@user_passes_test( admin_check )
def group_list( request ):
    """
    Lists all admin users with pagination, order by, search, etc. using www.datatables.net

    :param: request
    :return: String
    """

    context = {}
    return render( request, 'core/admin/group/list.html', context )


@restrict_internal_ips
@permission_required( 'auth.view_group', login_url = 'admin:login' )
@user_passes_test( admin_check )
def group_list_json( request ):
    """
    Generates JSON for the listing (required for the JS plugin www.datatables.net)

    :param: request
    :return: String
    """

    # Query data
    #group = Group()
    objects = Group.objects.all()

    # settings
    info = {
        'fields_to_select': [ 'id', 'name' ],
        'fields_to_search': [ 'id', 'name' ],
        'default_order_by': 'name',
        'url_base_name': 'group',
        'namespace': 'admin:core:',
    }

    #build json data and return it to the screen
    json = build_datatable_json( request, objects, info )
    return HttpResponse( json )

@restrict_internal_ips
@permission_required( 'auth.add_group', login_url = 'admin:login' )
@user_passes_test( admin_check )
def group_add( request ):
    """
    Add new Group

    :param: request
    :param: user_id
    :return: String
    """

    # When form is submitted
    if request.method == 'POST':

        # Tries to validate form and save data
        form = GroupForm( request.POST )
        if form.is_valid():
            group = form.save()
            messages.success( request, 'Group was successfully added.')
            return HttpResponseRedirect( reverse( 'admin:core:group_details', args = ( group.id, ) ) )

    else:
        form = GroupForm()

    # Template data
    context = { 'form': form, 'cancel_url': reverse( 'admin:core:groups' ) }

    # Print Template
    return render( request, 'core/admin/group/add.html', context )


@restrict_internal_ips
@permission_required( 'auth.view_group', login_url = 'admin:login' )
@user_passes_test( admin_check )
def group_details( request, group_id ):
    """
    View GROUP page

    :param: request
    :param: group_id
    :return: String
    """

    # Identify database record
    group = get_object_or_404( Group, pk = group_id )

    # Template data
    context = { 'group': group }

    # Print Template
    return render( request, 'core/admin/group/details.html', context )


@restrict_internal_ips
@permission_required( 'auth.edit_group', login_url = 'admin:login' )
@user_passes_test( admin_check )
def group_edit( request, group_id ):
    """
    Edit Group data

    :param: request
    :param: group_id
    :return: String
    """

    # Identify database record
    group = get_object_or_404( Group, pk = group_id )

    # When form is submitted
    if request.method == 'POST':

        # Tries to validate form and save data
        form = GroupForm( request.POST, instance = group )
        if form.is_valid():
            form.save()
            messages.success( request, 'Group was successfully updated.')
            return HttpResponseRedirect( reverse( 'admin:core:group_details', args = ( group_id, ) ) )

    else:
        form = GroupForm( instance = group )

    # Template data
    context = { 'form': form, 'cancel_url': reverse( 'admin:core:group_details', args = ( group_id, ) ) }

    # Print Template
    return render( request, 'core/admin/group/edit.html', context )


@restrict_internal_ips
@permission_required( 'auth.delete_group', login_url = 'admin:login' )
@user_passes_test( admin_check )
def group_delete( request, group_id ):
    """
    Delete Group action.

    :param: request
    :param: group_id
    :return: String
    """

    # Identify database record
    group = get_object_or_404( Group, pk = group_id )
    return HttpResponse( 'Deleted' )

    # mark as INACTIVE
    group.is_active = False
    group.save()

    # Redirect with success message
    messages.success( request, 'group was successfully marked as INACTIVE.')
    return HttpResponseRedirect( reverse( 'admin:core:admin_groups' ) )