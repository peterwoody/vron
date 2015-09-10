"""
Custom TEMPLATE CONTEXT PROCESSORS to be used by
https://docs.djangoproject.com/en/1.7/ref/settings/#std:setting-TEMPLATE_CONTEXT_PROCESSORS

If you need a global template variable (just like a constant) you can set the function here
and include on TEMPLATE_CONTEXT_PROCESSORS on settings.

"""

##########################
# Imports
##########################
from django.conf import settings





##########################
# Function definitions
##########################
def add_global_template_data( request ):

    template_data = {}

    # Determine if we are in PROD server or not
    template_data['is_prod'] = getattr( settings, 'IS_PROD', False )

    # Set destination country IDs
    template_data['ID_COUNTRY_AUSTRALIA'] = getattr( settings, 'ID_COUNTRY_AUSTRALIA', False )
    template_data['ID_COUNTRY_CANADA'] = getattr( settings, 'ID_COUNTRY_CANADA', False )

    # Full path
    template_data['relative_full_path'] = request.get_full_path()

    # Base URL
    protocol = 'https://' if request.is_secure else 'http://'
    template_data['base_url'] = protocol + request.get_host()

    # SQL Debug Mode (Get all executed SQL Queries)
    sql_debug_on = getattr( settings, 'SQL_DEBUG', False )
    if sql_debug_on:
        from django.db import connection
        queries_text = ''
        for query in connection.queries:
            queries_text += '<br /><br /><br /><br />' + str( query['sql'] )
            queries_text += '<br /><br /><strong>Time:</strong> ' + str( query['time'] )
        template_data['sql_output'] = queries_text

    return template_data