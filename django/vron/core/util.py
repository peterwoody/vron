"""
Custom functions not elsewhere classified.

We put here all functions that couldn't belong to any module or class.
"""

##########################
# Imports
##########################
from functools import reduce
from django.db.models import Q
import json
from django.core.urlresolvers import reverse
from django.shortcuts import _get_queryset
from calendar import monthrange
from datetime import date, datetime, timedelta
from django.http import HttpResponse
from django.db import models
from django.db.models.query import QuerySet
from operator import itemgetter





##########################
# Function definitions
##########################
def calculate_age( birth_date ):
    """
    Calculates age based on birth date

    :param birth_date:
    :return Int:
    """
    if not birth_date:
        return 0

    today = date.today()
    return today.year - birth_date.year - ( ( today.month, today.day) < ( birth_date.month, birth_date.day ) )


def date_difference( start_date, end_date, mode = 'months' ):
    """
    Calculates difference between 2 dates and return in mode (months or years)

    :param start_date:
    :param end_date:
    :param mode:
    :return Mixed:
    """
    months = 0
    while True:
        mdays = monthrange( start_date.year, start_date.month )[1]
        start_date += timedelta( days = mdays )
        if start_date <= end_date:
            months += 1
        else:
            break

    if mode == 'months':
        result = months
    elif mode == 'years':
        result = round( months / 12, 2 )

    return result


def date_range( start_date, end_date ):
    """
    Returns a generator for all dates between an start and end date given

    :param start_date:
    :param end_date:
    :return Mixed:
    """
    for n in range( int ( ( end_date - start_date ).days ) + 1 ):
        yield start_date + timedelta( n )

def convert_date_format( date, from_format, to_format ):
    """
    Formats a date from a given format to a new one

    :param date:
    :param from_format:
    :param to_format:
    :return Mixed:
    """
    date = datetime.strptime( date, from_format )
    return date.strftime( to_format )


def build_datatable_json( request, objects, info, support = ['edit', 'delete'] ):
    """
    Generates JSON for the listing (required for the JS plugin www.datatables.net)

    :param: request
    :param: objects
    :param: info
    :return: String
    """

    # options set
    list_display = info['fields_to_select']
    list_filter = info['fields_to_search']
    default_order_by = info['default_order_by']

    # count total items:
    total_records = objects.count()

    #filter on list_filter using __contains
    if request.method == 'GET' and 'sSearch' in request.GET:
        search = request.GET['sSearch']
        queries = [Q(**{f+'__contains' : search}) for f in list_filter]
        qs = reduce(lambda x, y: x|y, queries)
        objects = objects.filter(qs)

    #sorting
    order = dict( enumerate(list_display) )
    dirs = {'asc': '', 'desc': '-'}
    if request.method == 'GET' and 'sSortDir_0' in request.GET:
        field = order[int(request.GET['iSortCol_0'])]
        if '.' in field:
            field = field.replace( '.', '__' )
        order_by = dirs[request.GET['sSortDir_0']] + field
    else:
        order_by = default_order_by
    objects = objects.order_by( order_by )

    # count items after filtering:
    total_display_records = objects.count()

    # finally, slice according to length sent by dataTables:
    if request.method == 'GET' and 'iDisplayStart' in request.GET:
        start = int( request.GET['iDisplayStart'] )
    else:
        start = 0
    if request.method == 'GET' and 'iDisplayLength' in request.GET:
        length = int(request.GET['iDisplayLength'])
    else:
        length = 10
    objects = objects[ start : (start+length)]

    # build HTML for action buttons (delete, edit, view)
    edit_html = ''
    delete_html = ''
    if 'edit' in support:
        edit_html = """<li><a href="#edit_link#" class=""><i class="fa fa-edit"></i>Edit Data</a></li>"""
    if 1 == 1:
        delete_html = """<li><a href="#" onclick="javascript: confirm_delete( '#delete_link#'); "><i class="fa fa-trash-o"></i>Remove</a></li>"""

    base_buttons_html = """
                            <div class="btn-group btn-group-xs">
                                <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                                    <i class="fa fa-cog"></i>
                                    <i class="fa fa-caret-down"></i>
                                    <span class="sr-only">Toggle Dropdown</span>
                                </button>
                                <ul class="dropdown-menu left" role="menu">
                                    <li><a href="#details_link#" class=""><i class="fa fa-search"></i>View Details</a></li>
                                    """+edit_html+"""
                                    """+delete_html+"""
                                </ul>
                            </div>
                        """

    # extract information
    data = []
    for obj in objects:
        values = []
        for field in list_display:
            if '.' in field:
                split = field.split( '.' )
                sub_obj = getattr( obj, split[0] )
                value = getattr( sub_obj, split[1] )
                if 'prepend' in info and split[0] in info['prepend']:
                    value = info['prepend'][split[0]] + value
                values.append( str( value ) )
            else:
                value = getattr( obj, field )
                if 'prepend' in info and field in info['prepend']:
                    value = info['prepend'][field] + value
                values.append( str( value ) )
        buttons_html = base_buttons_html.replace( "#details_link#", reverse( info['namespace'] + info['url_base_name'] + '_details', args = ( obj.id, ) ) )
        if 'edit' in support:
            buttons_html = buttons_html.replace( "#edit_link#", reverse( info['namespace'] + info['url_base_name'] + '_edit', args = ( obj.id, ) ) )
        if 1 == 1:
            buttons_html = buttons_html.replace( "#delete_link#", reverse( info['namespace'] + info['url_base_name'] + '_delete', args = ( obj.id, ) ) )
        values.append( buttons_html )
        data.append( values )

    # sEcho variable
    if request.method == 'GET' and 'sEcho' in request.GET:
        sEcho = request.GET['sEcho']
    else:
        sEcho = ''

    #define response
    response = {
        'aaData': data,
        'iTotalRecords': total_records,
        'iTotalDisplayRecords': total_display_records,
        'sEcho':  sEcho
    }

    #serialize to json
    return json.dumps( response )


def get_object_or_false( klass, *args, **kwargs ):
    """
    Uses get() to return an object, or False if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    if 'no_query' in kwargs:
        try:
            return klass
        except klass.DoesNotExist:
            return False
    else:
        queryset = _get_queryset( klass )
        try:
            return queryset.get( *args, **kwargs )
        except queryset.model.DoesNotExist:
            return False


def get_list_or_false( klass, *args, **kwargs ):
    """
    Uses filter() to return a list of objects, or False if
    the list is empty.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the filter() query.
    """
    queryset = _get_queryset( klass )
    obj_list = list( queryset.filter( *args, **kwargs ) )
    if not obj_list:
        return False
    return obj_list





###########################
# DEBUGGING FUNCTIONS 
###########################
def dbg( var, depth = 0 ):
    """
    Show all 'var' content.
    :param: var The variable to be debugged.
    """

    # Predefined constants
    NEWLINE =  "<br>"
    TAB = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"

    result = ''

    # MODEL
    if isinstance( var, models.Model ):
        # Get all members of the class excluding functions and __etc__.
        fields = [ ( field.name, getattr( var, field.name ) ) for field in var._meta.fields ]
        result += "{0}[ {1} ( {2} attributes ) ]:{3}".format( ( TAB * depth ), var.__class__.__name__, len( fields ), NEWLINE )
        result += dbg( fields, depth + 1 )

    # LIST
    elif isinstance( var, list ) or isinstance( var, QuerySet ):
        result += "{0}[ {1} ( {2} items ) ]:{3}".format( ( TAB * depth ), var.__class__.__name__, len( var ), NEWLINE )
        for m in var:
            result += dbg( m, depth + 1 )

    # DICT, SET
    elif isinstance( var, dict ):
        result += "{0}[ {1} ( {2} attributes ) ]:{3}".format( ( TAB * depth ), var.__class__.__name__, len( var ), NEWLINE )

        # Shows all key-values of var.
        for k, v in var.items():
            result += "{0}[ {1} ]: {2}{3}".format( ( TAB * ( depth + 1 ) ), k, dbg( v, depth + 1 ), NEWLINE )

    # TUPLE
    elif isinstance( var, tuple ):
        result += "{0}[ {1} ] : {2}{3}".format( ( TAB * depth ), var[0], dbg( var[1], depth +1 ), NEWLINE )

    # PRIMITIVE
    else:
        result += "({0}) {1}".format( var.__class__.__name__, str( var ) ) + NEWLINE

    return result


def debug_sql():
    # Print SQL Queries
    from django.db import connection
    queries_text = ''
    for query in connection.queries:
        queries_text += '<br /><br /><br />' + str( query['sql'] )
    return HttpResponse( queries_text )