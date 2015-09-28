"""
Core model classes.

These are the models shared by all apps
"""

##########################
# Imports
##########################
from django.db import models
from vron.core.models import BaseModel





##########################
# Classes definitions
##########################
class Config( BaseModel ):
    """
    Stores VRON config data, such as viator api key, ron username, etc.
    """

    name = models.CharField( "option name", max_length = 100 )
    value = models.CharField( "option value", max_length = 100 )

    # META Options
    class Meta:
        default_permissions = []
        permissions = (
            ( "admin_add_config", "ADMIN: Can add config option" ),
            ( "admin_change_config", "ADMIN: Can change config option" ),
            ( "admin_delete_config", "ADMIN: Can delete config option" ),
            ( "admin_view_config", "ADMIN: Can view config options" ),
        )


class Key( BaseModel ):
    """
    Stores API keys following the format BASE_KEY + HOST_ID
    """

    name = models.CharField( "name", max_length = 20 )
    comments = models.CharField( "comments", max_length = 255, blank = True, null = True )

    # META Options
    class Meta:
        default_permissions = []
        permissions = (
            ( "admin_add_config", "ADMIN: Can add config option" ),
            ( "admin_change_config", "ADMIN: Can change config option" ),
            ( "admin_delete_config", "ADMIN: Can delete config option" ),
            ( "admin_view_config", "ADMIN: Can view config options" ),
            )


class Log( BaseModel ):
    """
    Stores every request received and set its status
    """

    external_reference = models.CharField( "external reference", max_length = 40, blank = True, null = True )
    log_status = models.ForeignKey( 'LogStatus' )
    error_message = models.TextField( "error message", blank = True, null = True )
    ron_confirmation_number = models.IntegerField( "confirmation number", blank = True, null = True )
    attempts = models.IntegerField( "attempts", default = 1 )

    # META Options
    class Meta:
        default_permissions = []
        permissions = (
            ( "admin_view_request", "ADMIN: Can view logs" ),
        )

    # Class Methods
    @staticmethod
    def get_listing():
        """
        Query used to search for logs joined with log_status

        :param: provider_id
        :return: Objects
        """

        logs = Log.objects.select_related(
            'log_status'
        ).only(
            'id', 'modified_date', 'external_reference', 'log_status__name',
            'ron_confirmation_number'
        ).order_by(
            '-id'
        )
        return logs

class LogStatus( BaseModel ):
    """
    The status of a request: 'complete', 'received', 'error on ron call', etc.
    """
    name = models.CharField( max_length = 50 )

    # META Options
    class Meta:
        default_permissions = []